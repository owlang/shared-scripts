#!/usr/bin/env python3
"""
hpa_extract-antigen-seq_from_xml.py
======================
Extract antigen (PrEST) sequences and gene-level metadata from a locally
downloaded Human Protein Atlas (HPA) XML file, for a user-provided list of HPA
antibody IDs (e.g. HPA077039).

Output is a TAB-DELIMITED file keyed on the HPA antibody id, with columns:
    hpa_id, name, synonyms, ensembl, uniprot, seq_length, antigen_sequence
A JSON file (matched records + missing ids + summary, including the XML schema
location/version) can optionally be written as well.

XML structure assumed (confirmed against HPA release 25 / schemaVersion 3.0):

    <proteinAtlas xsi:schemaLocation="...proteinatlas.xsd" schemaVersion="3.0">
      <entry>
        <name>TSPAN6</name>
        <synonym>T245</synonym>
        <synonym>TM4SF6</synonym>
        <identifier id="ENSG00000000003" db="Ensembl" ...>
          <xref id="O43657" db="Uniprot/SWISSPROT"/>
          <xref id="7105"   db="NCBI GeneID"/>
        </identifier>
        <antibody id="HPA077039">
          <antigenSequence>MKAVL...RST</antigenSequence>
        </antibody>
        ...
      </entry>
      ...
    </proteinAtlas>

DESIGN NOTES
------------
* Streaming parse (iterparse) with per-entry memory cleanup, so it handles the
  full multi-GB whole-atlas download (~13 GB / ~20k entries) at flat, low memory.
  After each <entry> is processed it is cleared AND removed from the root, so
  ElementTree does not accumulate empty element husks across the parse.
* Tag matching is namespace-insensitive (matches by local name), so a default or
  prefixed XML namespace on the root does not break <entry>/<antibody>/etc.
* Gene-level fields (<name>, <synonym>, <identifier>) are direct children of
  <entry> and are read once per entry, then attached to every matching antibody
  in that entry.
* UniProt accession: taken from an <identifier>/<xref> whose db starts with
  'Uniprot'; reviewed SWISSPROT is preferred over unreviewed TREMBL. The first
  matching accession is used (see read_entry_metadata to collect all instead).
* Ensembl gene id is the 'id' attribute of the <identifier> whose db == 'Ensembl'.
* An antibody that matches an id but has no <antigenSequence> is reported with an
  empty sequence (and flagged in the JSON summary), never silently dropped.
* Requested ids absent from the file are reported in the JSON 'missing_ids'.
* Nothing is invented: every value comes from the file or is left empty.

Requires: Python standard library only.

USAGE
-----
  python3 hpa_extract-antigen-seq_from_xml.py atlas.xml HPA077039 HPA001666 -o out.tsv
  python3 hpa_extract-antigen-seq_from_xml.py atlas.xml -i ids.txt -o out.tsv --json out.json
  python3 hpa_extract-antigen-seq_from_xml.py atlas.xml --all -o all.tsv
"""

import csv
import sys
import json
import argparse
import xml.etree.ElementTree as ET


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def localname(tag) -> str:
    """Return an element tag without any {namespace} prefix."""
    if not isinstance(tag, str):
        return str(tag)
    return tag.rsplit("}", 1)[-1]


def read_root_metadata(xml_path):
    """Read schemaLocation and schemaVersion from the root <proteinAtlas> element.

    Uses the first 'start' event so the root is available before the body is
    parsed. Attribute names are matched by local name, so xsi:schemaLocation
    (which becomes '{http://...}schemaLocation' after parsing) is found
    regardless of the namespace prefix.
    """
    schema_location = None
    schema_version = None
    try:
        for _event, elem in ET.iterparse(xml_path, events=("start",)):
            for key, val in elem.attrib.items():
                lname = localname(key)
                if lname == "schemaLocation":
                    schema_location = (val or "").strip() or None
                elif lname == "schemaVersion":
                    schema_version = (val or "").strip() or None
            break  # only the root is needed
    except ET.ParseError:
        pass  # leave as None; the main parse surfaces any real error
    return schema_location, schema_version


def find_antigen_sequence(antibody_el):
    """Return the <antigenSequence> text within an <antibody> subtree, or None.

    Searches the whole subtree so it works whether the sequence sits directly
    under <antibody> or inside a wrapper element.
    """
    for el in antibody_el.iter():
        if localname(el.tag) == "antigenSequence":
            txt = (el.text or "").strip()
            return txt if txt else None
    return None


def read_entry_metadata(entry_el):
    """Extract gene-level fields that are direct children of <entry>.

    Returns dict: name, synonyms (';'-joined or None), ensembl, uniprot.
    """
    name = None
    synonyms = []
    ensembl = None
    uniprot_swissprot = None
    uniprot_other = None

    for child in entry_el:  # direct children only
        ln = localname(child.tag)
        if ln == "name" and name is None:
            name = (child.text or "").strip() or None
        elif ln == "synonym":
            syn = (child.text or "").strip()
            if syn:
                synonyms.append(syn)
        elif ln == "identifier":
            # Ensembl gene id is on the <identifier> element itself
            if (child.get("db") or "") == "Ensembl" and ensembl is None:
                ensembl = (child.get("id") or "").strip() or None
            # UniProt accessions are in <xref> children
            for xref in child:
                if localname(xref.tag) != "xref":
                    continue
                db = (xref.get("db") or "")
                if db.startswith("Uniprot"):
                    acc = (xref.get("id") or "").strip()
                    if not acc:
                        continue
                    if "SWISSPROT" in db.upper() and uniprot_swissprot is None:
                        uniprot_swissprot = acc
                    elif uniprot_other is None:
                        uniprot_other = acc

    return {
        "name": name,
        "synonyms": ";".join(synonyms) if synonyms else None,
        "ensembl": ensembl,
        "uniprot": uniprot_swissprot or uniprot_other,
    }


def iter_antibodies(xml_path):
    """Stream <entry> elements, yielding
        (entry_index, entry_meta, antibody_id, antigen_sequence_or_None)
    for every <antibody>, with per-entry memory cleanup for very large files.

    Assumes <entry> elements are direct children of the root <proteinAtlas>
    (true for the HPA download). After each entry is processed it is cleared and
    removed from the root so memory stays flat across a multi-GB parse.
    """
    context = ET.iterparse(xml_path, events=("start", "end"))
    _event, root = next(context)  # root element from the first 'start' event
    entry_index = 0
    for event, elem in context:
        if event != "end" or localname(elem.tag) != "entry":
            continue
        entry_index += 1
        entry_meta = read_entry_metadata(elem)
        for desc in elem.iter():
            if localname(desc.tag) == "antibody":
                ab_id = desc.get("id")
                if not ab_id:  # fallback: id carried in a child element
                    for c in desc:
                        if localname(c.tag) in ("id", "antibodyId"):
                            ab_id = (c.text or "").strip()
                            break
                seq = find_antigen_sequence(desc)
                yield entry_index, entry_meta, ab_id, seq
        elem.clear()
        # The finished entry is the leading child of root; drop it to free memory.
        del root[0]


# ---------------------------------------------------------------------------
# output
# ---------------------------------------------------------------------------
TSV_COLUMNS = ["hpa_id", "name", "synonyms", "ensembl",
               "uniprot", "seq_length", "antigen_sequence"]


def write_tsv(path, results):
    """Write results as a tab-delimited file keyed on the HPA antibody id.

    csv.writer with QUOTE_MINIMAL safely quotes any field that happens to
    contain a tab or newline. Missing values are written as empty strings.
    """
    with open(path, "w", newline="") as f:
        w = csv.writer(f, delimiter="\t", quoting=csv.QUOTE_MINIMAL,
                       lineterminator="\n")
        w.writerow(TSV_COLUMNS)
        for r in results:
            w.writerow([("" if r.get(c) is None else r.get(c)) for c in TSV_COLUMNS])


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(
        description="Extract antigen sequences + metadata from a local HPA XML "
                    "file for a list of HPA antibody ids. Output is TSV keyed on "
                    "the HPA id; JSON summary is optional.")
    ap.add_argument("xml", help="Path to the downloaded HPA .xml file")
    ap.add_argument("ids", nargs="*", help="HPA antibody ids, e.g. HPA077039")
    ap.add_argument("-i", "--input",
                    help="File with one HPA id per line (# comments allowed)")
    ap.add_argument("--all", action="store_true",
                    help="Ignore the id list; emit every antibody that has a sequence")
    ap.add_argument("-o", "--output", required=True,
                    help="Path for the tab-delimited output file")
    ap.add_argument("--json",
                    help="Optional path to also write a JSON summary "
                         "(matched records, missing ids, schema info)")
    args = ap.parse_args()

    # Increment for displaying progress
    nprogress = 200

    # build the wanted-id set (uppercased for case-insensitive matching)
    wanted = {x.strip().upper() for x in args.ids if x.strip()}
    if args.input:
        try:
            with open(args.input) as f:
                for ln in f:
                    ln = ln.strip()
                    if ln and not ln.startswith("#"):
                        wanted.add(ln.upper())
        except FileNotFoundError:
            sys.exit(f"Id list not found: {args.input}")
    if not args.all and not wanted:
        ap.error("Provide HPA ids (positional or --input), or use --all.")

    # fail early and cleanly if the XML file is missing/unreadable
    try:
        open(args.xml, "rb").close()
    except OSError as e:
        sys.exit(f"Cannot open XML file '{args.xml}': {e}")

    # read schema metadata (cheap separate pass over just the root element)
    schema_location, schema_version = read_root_metadata(args.xml)

    results = []
    found_ids = set()
    total_antibodies = 0
    matched_without_seq = 0

    try:
        for entry_i, meta, ab_id, seq in iter_antibodies(args.xml):
            total_antibodies += 1
            if total_antibodies % nprogress == 0:
                # \r keeps it on one updating line instead of flooding stderr
                print(f"\r  ...processed {total_antibodies:,} antibodies "
                      f"({len(results):,} matched)", end="", file=sys.stderr, flush=True)
            if ab_id is None:
                continue

            if args.all:
                if seq:
                    results.append({
                        "hpa_id": ab_id, "entry_index": entry_i,
                        "name": meta["name"], "synonyms": meta["synonyms"],
                        "ensembl": meta["ensembl"], "uniprot": meta["uniprot"],
                        "antigen_sequence": seq, "seq_length": len(seq),
                    })
                continue

            ab_up = ab_id.upper()
            if ab_up in wanted:
                found_ids.add(ab_up)
                rec = {
                    "hpa_id": ab_id, "entry_index": entry_i,
                    "name": meta["name"], "synonyms": meta["synonyms"],
                    "ensembl": meta["ensembl"], "uniprot": meta["uniprot"],
                    "antigen_sequence": seq,
                    "seq_length": len(seq) if seq else None,
                }
                if seq is None:
                    rec["note"] = "antibody matched but no <antigenSequence> in its subtree"
                    matched_without_seq += 1
                results.append(rec)
    except ET.ParseError as e:
        sys.exit(f"XML parse error: {e}\n(Is the file complete / valid XML?)")
    except FileNotFoundError:
        sys.exit(f"XML file not found: {args.xml}")

    # close off the in-place progress line with a newline
    if total_antibodies >= nprogress:
        print(f"\r  ...processed {total_antibodies:,} antibodies "
              f"({len(results):,} matched)", file=sys.stderr, flush=True)

    missing = sorted(wanted - found_ids) if not args.all else []

    # ---- TSV (primary output) ----
    write_tsv(args.output, results)
    print(f"Wrote TSV -> {args.output}  ({len(results)} rows)", file=sys.stderr)

    # ---- JSON (optional) ----
    if args.json:
        payload = {
            "matched": results,
            "missing_ids": missing,
            "summary": {
                "schema_location": schema_location,
                "schema_version": schema_version,
                "antibodies_scanned": total_antibodies,
                "requested": (None if args.all else len(wanted)),
                "matched": len(results),
                "matched_without_sequence": matched_without_seq,
                "missing": len(missing),
            },
        }
        with open(args.json, "w") as f:
            json.dump(payload, f, indent=2)
        print(f"Wrote JSON -> {args.json}", file=sys.stderr)

    # ---- human-readable summary ----
    print(
        f"\nSchema: {schema_version or '?'} ({schema_location or 'n/a'})\n"
        f"Scanned {total_antibodies} antibody elements. "
        f"Matched {len(results)}"
        + ("" if args.all else f" of {len(wanted)} requested")
        + f"; {matched_without_seq} matched without a sequence; "
          f"{len(missing)} requested ids not found.",
        file=sys.stderr,
    )
    if missing:
        preview = ", ".join(missing[:20]) + (" ..." if len(missing) > 20 else "")
        print(f"Missing ids: {preview}", file=sys.stderr)


if __name__ == "__main__":
    main()