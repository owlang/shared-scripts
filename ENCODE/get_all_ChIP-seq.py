import argparse
import json
import requests

# Info we want:
# Histone and TF (No IgG) in K562
# BAM (hgXX) download URL
# Metadata...ENCSR, ENCFF, Rep#


# Filter weird conditions...
# Get only replicate 1 (or deeper seq?)
# CRISPR okay...
# Skip audit orange?

def getParams():
    '''Parse parameters from the command line'''
    parser = argparse.ArgumentParser(description='Retrieve ENCODE metadata from API for all Histone and TF ChIP-seq in K562.')

    # parser.add_argument('-i','--input', metavar='input_fn', required=True, help='the tab-delimited file with ENCFF accessions of BAM files in the first column')
    parser.add_argument('-o','--output', metavar='tab_fn', required=True, help='the output tsv filename')

    args = parser.parse_args()
    return(args)


# Helper: ENCFF to URL to payload
def fetch_data(url):
    # Force return from the server in JSON format
    headers = {'accept': 'application/json'}

    # GET the search result
    response = requests.get(url, headers=headers)

    # Extract the JSON response as a python dictionary
    search_results = response.json()
    return(search_results)


# Main program which takes in input parameters
if __name__ == '__main__':

    # Get params
    args = getParams()

    # All ENCSR accessions filtered such that
    # - assay = "TF ChIP-seq" or "Histone ChIP-seq"
    # - biosample = "K562" and "not perturbed"
    # - genome build = "GRCh38"
    all_ChIP_URL="https://www.encodeproject.org/search/?type=Experiment&control_type%21=%2A&status=released&assay_title=TF+ChIP-seq&assay_title=Histone+ChIP-seq&biosample_ontology.term_name=K562&assembly=GRCh38&perturbed=false&format=json&limit=all"

    # All ENCFF accessions filtered such that
    # - assay = "TF ChIP-seq" or "Histone ChIP-seq"
    # - biosample = "K562"
    # - genome build = "GRCh38"
    # - did not filter for "not perturbed"
    all_ChIP_BAM_URL="https://www.encodeproject.org/search/?type=File&file_format=bam&assay_title=TF+ChIP-seq&assay_title=Histone+ChIP-seq&biosample_ontology.term_name=K562&assembly=GRCh38&format=json&limit=all"

    # Get payload for accession
    data = fetch_data(all_ChIP_BAM_URL)['@graph']

    # Initialize storage variable
    target2info = {}

    # Extract data from each hit
    for json in data:

        # Save Target, download_url, ENCSR, ENCFF, replicate number, run_type, sequencing depth to target info

        # Check for existing target entry
        # Is mine "better"?

        # Update if so...

    # Write metadata with download URL
    [ sys.stdout.write('\t'.join(info) + "\n") for info in target2info.values() ]
