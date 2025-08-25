import argparse
import json
import requests

# Data links:
# - https://rest.ensembl.org/archive/id/ENSG00000170312?content-type=application/json
# - https://rest.ensembl.org/lookup/id/ENSG00000170312?expand=1;content-type=application/json
# - https://rest.ensembl.org/lookup/id/ENSG00000170312?content-type=application/json

# Documentation links:
# - https://rest.ensembl.org/

def getParams():
    '''Parse parameters from the command line'''
    parser = argparse.ArgumentParser(description = """
============
Retrieve Ensembl metadata for a list of ENSG accessions.
============
""", formatter_class = argparse.RawTextHelpFormatter)

    parser.add_argument('-i','--input', metavar='txt_fn', required=True, help='the list of ENSG accessions to pull info for(first col tab-delimited).')
    parser.add_argument('-o','--output', metavar='tsv_fn', required=True, help='the output tab-delimited accessions and relevant metadata')

    args = parser.parse_args()
    return(args)

def fetch_data(ensg_list):

    # Build string from list of ids
    list_str = ','.join(f"\"{id}\"" for id in ensg_list)

    # Build post request
    server = "https://rest.ensembl.org"
    ext = "/lookup/id"
    headers={ "Content-Type" : "application/json", "Accept" : "application/json"}

    # POST
    r = requests.post(server+ext, headers=headers, data='{ "ids" : [' + list_str + '] }')

    if not r.ok:
        r.raise_for_status()
        raise Exception(f"Some sort of request error encountered")

    payload = r.json()
    # print(repr(payload))
    return(payload)

# {
#   "ENSG00000157764": {
#     "logic_name": "ensembl_havana_gene_homo_sapiens",
#     "seq_region_name": "7",
#     "source": "ensembl_havana",
#     "assembly_name": "GRCh38",
#     "object_type": "Gene",
#     "canonical_transcript": "ENST00000646891.2",
#     "species": "homo_sapiens",
#     "start": 140719327,
#     "strand": -1,
#     "version": 14,
#     "description": "B-Raf proto-oncogene, serine/threonine kinase [Source:HGNC Symbol;Acc:HGNC:1097]",
#     "db_type": "core",
#     "end": 140924929,
#     "biotype": "protein_coding",
#     "id": "ENSG00000157764",
#     "display_name": "BRAF"
#   },
#   "ENSG00000248378": {
#     "logic_name": "havana_homo_sapiens",
#     "seq_region_name": "5",
#     "source": "havana",
#     "version": 1,
#     "db_type": "core",
#     "canonical_transcript": "ENST00000515358.1",
#     "species": "homo_sapiens",
#     "description": "novel transcript",
#     "assembly_name": "GRCh38",
#     "object_type": "Gene",
#     "end": 31744451,
#     "biotype": "lncRNA",
#     "id": "ENSG00000248378",
#     "start": 31743988,
#     "strand": -1
#   }
# }

# Main program which takes in input parameters
if __name__ == '__main__':

    # Get params
    args = getParams()

    # Load ENSG accessions
    with open(args.input, 'r') as f:
        ensg_list = [line.strip().split('\t')[0] for line in f]

    # Get payload for accessions
    payload = fetch_data(ensg_list)

    # Initialize line storage
    lines = []

    # Parse payload for each accession
    for ensg in ensg_list:

        data = payload[ensg]

        display_name = data.get('display_name', '')

        # Update lines with new metadata
        row = [ensg, display_name, data['biotype'], data['db_type'], data['source'], data['species'], data['description']]

        lines.append('\t'.join([str(i) for i in row]))

    headers = ["accession", "display_name", "biotype", "db_type", "source", "species", "description"]
    # Writing to sample.json
    with open(args.output, "w") as outfile:
        outfile.write('\t'.join(headers) + "\n")
        outfile.write('\n'.join(lines))
