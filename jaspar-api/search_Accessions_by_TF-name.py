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
Retrieve JASPAR motifs as a list of JASPAR accessions (MA###.#) based on matches to an input list of TF/target names.

Note: If you want to pull all versions of a motif, please make sure you use the '--all' flag
============
""", formatter_class = argparse.RawTextHelpFormatter)

    parser.add_argument('-i','--input', metavar='names_fn', required=True, help='the tsv file with first column of target/TF names')
    parser.add_argument('-o','--output', metavar='tsv_fn', required=True, help='the output text file list of accessions and target info')
    
    parser.add_argument('--all', action='store_true', help='return all versions of the motif')
    parser.add_argument('-j','--jdb-version', metavar='jdb_version_string', default=None, choices=['JASPAR2024', 'JASPAR2022', 'JASPAR2020', 'JASPAR2018', 'JASPAR2016', 'JASPAR2014'], help='the JASPAR version to query (defaults to most recent)')
    # Update choices with available releases:
    # You can find the available releases/version of JASPAR using get_releases method.
    # print(jdb_obj.get_releases())
    # Just add missing strings to "choices" in CLI to update

    args = parser.parse_args()
    return(args)


# Main program which takes in input parameters
if __name__ == '__main__':

    # Get params
    args = getParams()

    # Get JASPAR db object
    jdb_obj = jaspardb()
    if (args.jdb_version != None):
        jdb_obj = jaspardb(release=args.jdb_version)

    # Extract name list
    reader = open(args.input, 'r')
    qnames_list = [line.strip().split('\t')[0] for line in reader]
    reader.close()

    # Initialize storage obj
    fields = []

    # Query each name extracted from input list
    for query_name in qnames_list:
        print(query_name)
        # Fetch motif by parsed accession
        motifs = jdb_obj.fetch_motifs(tf_name=query_name, all_versions=args.all)
        # Parse info from each motif match
        for m in motifs:
            # Extract and list out fields to include
            fields.append([m.matrix_id, query_name, m.name, jdb_obj.release])

    # Sort results
    fields.sort(key=lambda x: (x[1], x[0]))

    # Open writer
    writer = open(args.output, 'w')

    # Write output header
    header = ["matrix_id", "input_query_name", "JASPAR_target_name", "JASPAR_Release"]
    writer.write("%s\n" % "\t".join(header))

    # Write output fields
    lines = ["\t".join(f) for f in fields]
    writer.write("\n".join(lines))

    # Close writer
    writer.close()


        
