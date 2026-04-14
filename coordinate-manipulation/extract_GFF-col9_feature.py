import argparse
import re

# #description: evidence-based annotation of the human genome (GRCh38), version 38 (Ensembl 104), mapped to GRCh37 with gencode-backmap
# #provider: GENCODE
# #contact: gencode-help@ebi.ac.uk
# #format: gff3
# #date: 2021-03-12
# chr1    HAVANA  gene    11869   14409   .       +       .       gene_id "ENSG00000223972.5_5"; gene_type "transcribed_unprocessed_pseudogene"; gene_name "DDX11L1"; level 2; hgnc_id "HGNC:37102"; havana_gene "OTTHUMG00000000961.2_5"; remap_status "full_contig"; remap_num_mappings 1; remap_target_status "overlap";
# chr1    HAVANA  transcript      11869   14409   .       +       .       gene_id "ENSG00000223972.5_5"; transcript_id "ENST00000456328.2_1"; gene_type "transcribed_unprocessed_pseudogene"; gene_name "DDX11L1"; transcript_type "processed_transcript"; transcript_name "DDX11L1-202"; level 2; transcript_support_level 1; hgnc_id "HGNC:37102"; tag "basic"; havana_gene "OTTHUMG00000000961.2_5"; havana_transcript "OTTHUMT00000362751.1_1"; remap_num_mappings 1; remap_status "full_contig"; remap_target_status "overlap";
# chr1    HAVANA  exon    11869   12227   .       +       .       gene_id "ENSG00000223972.5_5"; transcript_id "ENST00000456328.2_1"; gene_type "transcribed_unprocessed_pseudogene"; gene_name "DDX11L1"; transcript_type "processed_transcript"; transcript_name "DDX11L1-202"; exon_number 1; exon_id "ENSE00002234944.1_1"; level 2; transcript_support_level 1; hgnc_id "HGNC:37102"; tag "basic"; havana_gene "OTTHUMG00000000961.2_5"; havana_transcript "OTTHUMT00000362751.1_1"; remap_original_location "chr1:+:11869-12227"; remap_status "full_contig";

def getParams():
    '''Parse parameters from the command line'''
    parser = argparse.ArgumentParser(description='''
This script extracts the col 9 from a GTF/GFF3 file and splits the features separated by the ";" delimiter
- ignore comments (fields that start with '#')
- split fields by ";" and strip whitespace before and after quotation marks stripped
- (--query or --query-by-type): optionally survey the file for what features are available
                                                              
Examples:
    python extract_GFF-col9_feature.py -i COORD.gff --key gene_id -o VALUES.txt
    python extract_GFF-col9_feature.py -i COORD.gff --key gene_id --default None -o VALUES.txt
    python extract_GFF-col9_feature.py -i COORD.gff --query -o SurveyAll.txt              
    python extract_GFF-col9_feature.py -i COORD.gff --query-by-type -o SurveyTypes.txt   
''')
    parser.add_argument('-i','--input', metavar='gfffile', required=True, help='a GFF file to extract feature information from')
    parser.add_argument('-o','--output', metavar='outfile', required=True, help='a TXT file of the feature value (in order of input)')
    parser.add_argument('--key', default=None, help='the \'<key>=XYZ;\' indicating the feature field to keep (ignore quotations and bordering whitespace)')
    parser.add_argument('--default', default="", help='Value to report if none found by key')

    # "dry run" modes
    parser.add_argument('--query', action='store_true', help='query the gff file for possible feature keys')
    parser.add_argument('--query-by-type', action='store_true', help='query the gff file for possible feature keys (grouped by type)')

    args = parser.parse_args()
    return(args)

def strip_quotes(string):

    p_stripquotes = re.compile(r'^"(.+)"$')
    mgroups = re.search(p_stripquotes, string.strip())
    if mgroups:
        return(mgroups.group(1).strip())
    return string.strip()


if __name__ == "__main__":
    '''Write BED file in new order.'''

    # Parse params
    args = getParams()

    # Fast fail
    if args.key:
        assert args.key != "", "Key must be a non-empty string"
    else:
        assert args.query or args.query_by_type, "Key must be specified unless running a query on gff (--query or --query-by-type)"
        assert not (args.query and args.query_by_type), "Specify only --query or only --query-by-type"

    # For query
    type2feature_set = None
    if args.query or args.query_by_type:
        type2feature_set = {}

    # Open file handles
    reader = open(args.input, 'r')
    writer = open(args.output, 'w')
    for line in reader:
        # Skip comments
        if line.startswith('#'):
            continue
        tokens = line.strip().split('\t')

        # Confirm 9 columns
        assert len(tokens) == 9, f"A proper GFF/GTF file has 9 columns: {line}"

        # Split feature values by ";"
        features = tokens[8].strip().split(';')

        # Set defaults
        ret_value = args.default
        key_set = set()

        # Use "=" to delimit key-value pairs
        for f in features:
            # Skip empty features
            if f.strip() == "":
                continue

            # Parse out key and value
            pattern = re.compile(r'^(.+)[\s=]+(.+)$')
            mgroups = re.search(pattern, f.strip())
            key = strip_quotes(mgroups.group(1))
            value = strip_quotes(mgroups.group(2))

            # # Debug
            # print(f"--{f.strip()}--")
            # print(mgroups.group(1) + " --> " + key)
            # print(mgroups.group(2) + " --> " + value)

            # Update if feature key
            if key==args.key:
                ret_value = value

            # (Query) update key set
            key_set.add(key)

        if args.query or args.query_by_type:
            # Query updates - set default and update with latest
            type2feature_set.setdefault(tokens[2], set())
            type2feature_set[tokens[2]].update(key_set)
        else:
            # Write return value if not query
            writer.write(f"{ret_value}\n")
        

    # print(sorted(type2feature_set.keys()))
    if args.query_by_type:
        for t in sorted(type2feature_set.keys()):
            writer.write(f"{t}\n\t")
            writer.write("\n\t".join(sorted(list(type2feature_set[t]))))
            writer.write("\n")
    elif args.query:
        union = set()
        # Union all types for general query
        [ union.update(type2feature_set[t]) for t in type2feature_set.keys() ]
        writer.write("\n".join([s for s in union]))

    # Close file handles
    writer.close()
    reader.close()
