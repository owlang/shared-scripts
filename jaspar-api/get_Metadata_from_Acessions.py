import argparse
from pyjaspar import jaspardb

# https://pyjaspar.readthedocs.io/en/latest/how_to_use.html#get-motifs-by-tf-name

# Dependencies:
#   - pyjaspar

# conda install bioconda::pyjaspar

def getParams():
    '''Parse parameters from the command line'''
    parser = argparse.ArgumentParser(description = """
============
Retrieve JASPAR metadata from a list of JASPAR accessions (MA###.#).

List of fields retrieved:
   - matrix_id (input query list)
   - name
   - is_dimer (check for "::" string in name)
   - tf_class (list of strings, ";" delimited)
   - tf_family_list (list of strings, ";" delimited)
   - species (list of strings, ";" delimited)
   - tax_group
   - data_type
   - acc_list (like UniProt accessions)
   - length (of motif)
   - comment

Note: "species" returns taxon ids. You can look them up here: https://www.ncbi.nlm.nih.gov/taxonomy/?term=
============
""", formatter_class = argparse.RawTextHelpFormatter)

    parser.add_argument('-i','--input', metavar='samples_fn', required=True, help='the tsv file with first column of JASPAR accession codes.')
    parser.add_argument('-o','--output', metavar='tsv_fn', required=True, help='the output tab-delimited accessions and relevant metadata')

    # parser.add_argument('-j','--jdb-version', metavar='jdb_version_string', default=None, choices=['JASPAR2022', 'JASPAR2020', 'JASPAR2018', 'JASPAR2016', 'JASPAR2014'], help='the JASPAR version to query')
    # Update choices with available releases:
    # You can find the available releases/version of JASPAR using get_releases method.
    # print(jdb_obj.get_releases())
    # Just add missing strings to "choices" in CLI to update

    args = parser.parse_args()
    return(args)

def search_motifs(tf_str, jdb_obj):

    # Motifs
    motifs = jdb_obj.fetch_motifs_by_name("CTCF")
    print(len(motifs))


# Main program which takes in input parameters
if __name__ == '__main__':

    # Get params
    args = getParams()
    args.jdb_version = None # Remove when i figure out how i want to handle different db versions (if we want to handle this at all)

    # Get JASPAR db object
    jdb_obj = jaspardb()
    if (args.jdb_version != None):
        jaspardb(release=args.jdb_version)

    # Initialize file objects
    writer = open(args.output, 'w')
    reader = open(args.input, 'r')

    # Write output tsv column header
    header = ["matrix_id", "name", "is_dimer", "tf_class_list", "tf_family_list", "species_list", "tax_group", "data_type", "acc_list", "length", "comment"]
    writer.write("%s\n" % "\t".join(header))

    # Iterate through sample list
    for line in reader:

        # Read accession
        accession = line.strip().split('\t')[0]
        print(accession)

        # Fetch motif by parsed accession
        motif = jdb_obj.fetch_motif_by_id(accession)
        # print(motif)

        # TF name YY1
        # Matrix ID       MA0095.2
        # Collection      CORE
        # TF class        ['C2H2 zinc finger factors']
        # TF family       ['More than 3 adjacent zinc finger factors']
        # Species 9606
        # Taxonomic group vertebrates
        # Accession       ['P25490']
        # Data type used  ChIP-seq
        # Medline 18950698
        # Matrix:
        #         0      1      2      3      4      5      6      7      8      9     10     11
        # A: 1126.00 6975.00 6741.00 2506.00 7171.00   0.00  11.00  13.00 812.00 867.00 899.00 1332.00
        # C: 4583.00   0.00  99.00 1117.00   0.00  12.00   0.00   0.00 5637.00 1681.00 875.00 4568.00
        # G: 801.00 181.00 268.00 3282.00   0.00   0.00 7160.00 7158.00  38.00 2765.00 4655.00 391.00
        # T: 661.00  15.00  63.00 266.00   0.00 7159.00   0.00   0.00 684.00 1858.00 742.00 880.00

        # Check if JAPSAR target is a dimer
        is_dimer = "dimer" if motif.name.find("::") >= 0 else "-"

        # Extract and list out metadata to include
        metadata = [motif.matrix_id, motif.name, is_dimer, ";".join(motif.tf_class), ";".join(motif.tf_family), ";".join(motif.species), motif.tax_group, motif.data_type, ";".join(motif.acc), str(motif.length), motif.comment]
        metadata = ["" if val==None else val for val in metadata]
        # print(metadata)
        # to pull more info, read about the BioPython JASPAR motif record object: https://biopython.org/docs/1.75/api/Bio.motifs.jaspar.html

        # Write metadata to output
        writer.write("%s\n" % "\t".join(metadata))

    # Close file objects
    reader.close()
    writer.close()
