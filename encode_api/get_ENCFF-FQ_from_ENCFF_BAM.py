import argparse
import json
import requests

def getParams():
    '''Parse parameters from the command line'''
    parser = argparse.ArgumentParser(description = """
============
Retrieve ENCODE metadata of ENCFF FASTQ files from a list of ENCFF accessions of BAM files.
============
""", formatter_class = argparse.RawTextHelpFormatter)

    parser.add_argument('-i','--input', metavar='accession_fn', required=True, help='the text file of ENCFF accessions (BAM-type).')
    parser.add_argument('-o','--output', metavar='tsv_fn', required=True, help='the output tab-delimited accessions and relevant metadata')

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

    # Get payload for search
    payload = fetch_data(args.input)
    payload = payload.get("@graph", None)
    if (payload == None):
        print("Error: Returned JSON without \"@graph\"")
        quit()
    # print(json.dumps(data,indent=4))
    # quit()

    # Initialize line_storage
    lines = []

    # Parse text file for each accession
    reader = open(args.input, 'r')
    for line in reader:

        # Save BAM accession
        accession = line.strip().split('\t')[0]

        # Get BAM file payload
        bam_url = "https://www.encodeproject.org/file/" + accession + "?format=json"
        data = fetch_data(bam_url)

        # Check BAM file payload
        if (data == None):
            print("Error: File %s returned empty JSON. Skipping..." % accession)
            continue
        if (data.get('file_format', None) != "bam"):
            print("File %s is not a BAM file! Skipping..." % accession)
            continue

        schema_version = data.get('schema_version',"No Schema Version")
        print("====== %s ======" % accession)
        print("v%s" % schema_version)

        # Get Experiment Accession
        ENCSR = data.get('dataset', None)
        # Get replicate info
        mapped_run_type = data.get('mapped_run_type', None)  # single-ended, paired-ended
        biological_replicates = data.get('biological_replicates', ["-1"])[0]
        technical_replicates = data.get('technical_replicates', ["-1"])[0]

        # Get Sequencing Spec Info
        mapped_read_length = data.get('mapped_read_length', None)  # 36, 101
        # Get Biosample name
        strain = data.get('biosample_ontology', {}).get('@id', None)
        term_name = data.get('biosample_ontology', {}).get('term_name', None)
        # Get Assay
        assay_title = data.get('assay_title', None)
        # Get Target
        target = data.get('target',None)


        # Get Library accession
        # ENCLB = data.get('replicate',{'library':{'accession':None}})['library']['accession']
        # print(ENCLB)

        # Future work: add audit information

        # Get info derived from FASTQ
        FQ1 = FQ2 = md5sum1 = md5sum2 = platform = platform_name = perturbed = None
        for dfile in data.get("derived_from",[]):
            durl = "https://www.encodeproject.org" + dfile + "?format=json"
            ddata = fetch_data(durl)
            file_format = ddata.get('file_format', None)
            if (file_format == 'fastq'):
                if (mapped_run_type == 'single-ended'):
                    FQ1 = ddata.get('accession', None)
                    platform = data.get('platform', {}).get('@id', None)
                    platform_name = data.get('platform', {}).get('title', None)
                    md5sum1 = ddata.get('md5sum', None)
                    break
                paired_end = ddata.get('paired_end')
                if (paired_end == '1'):
                    FQ1 = ddata.get('accession', None)
                    platform = data.get('platform', {}).get('@id', None)
                    platform_name = data.get('platform', {}).get('title', None)s
                    md5sum1 = ddata.get('md5sum', None)
                if (paired_end == '2'):
                    FQ2 = ddata.get('accession', None)
                    md5sum2 = ddata.get('md5sum', None)


        # Update lines with new metadata
        row = [accession, mapped_run_type, FQ1, FQ2, md5sum1, md5sum2, ENCSR, mapped_read_length, platform, platform_name, biological_replicate, technical_replicates, strain, assay_title, target]

        lines.append('\t'.join([str(i) for i in row]))
    reader.close()

    headers = ["accession_bam", "mapped_run_type", "FQ1", "FQ2", "md5sum1", "md5sum2", "ENCSR", "mapped_read_length", "platform", "platform_name", "biological_replicate", "technical_replicates", "strain", "assay_title", "target"]
    # Writing to sample.json
    with open(args.output, "w") as outfile:
        outfile.write('\t'.join(headers) + "\n")
        outfile.write('\n'.join(lines))
