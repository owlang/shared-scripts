import argparse
from pyjaspar import jaspardb
from Bio.motifs import jaspar as pyj

# https://pyjaspar.readthedocs.io/en/latest/how_to_use.html#get-motifs-by-tf-name

# Dependencies:
#   - pyjaspar

# conda install bioconda::pyjaspar

def getParams():
    '''Parse parameters from the command line'''
    parser = argparse.ArgumentParser(description = """
============
Retrieve JASPAR position weight matrices (PWM) from a list of JASPAR accessions (MA###.#).

Each unique accession will have a new PWM file written to the working directory.
============
""", formatter_class = argparse.RawTextHelpFormatter)

    parser.add_argument('-i','--input', metavar='samples_fn', required=True, help='the tsv file with first column of JASPAR accession codes.')

    parser.add_argument('-f','--format', metavar='format_string', default='meme', choices=['pfm','jaspar','meme'], help='the PWM/PFM format for writing the output')
    parser.add_argument('-j','--jdb-version', metavar='jdb_version_string', default=None, choices=['JASPAR2024', 'JASPAR2022', 'JASPAR2020', 'JASPAR2018', 'JASPAR2016', 'JASPAR2014'], help='the JASPAR version to query (defaults to most recent)')
    # Update choices with available releases:
    # You can find the available releases/version of JASPAR using get_releases method.
    # print(jdb_obj.get_releases())
    # Just add missing strings to "choices" in CLI to update

    args = parser.parse_args()
    return(args)

def get_meme_formatted_str(motif):
    '''Write a Bio.motifs.jaspar.Motif object to a minimal MEME v4 string'''

    ALPHABET = 'ACGT'
    BFREQ = 'A 0.303 C 0.183 G 0.209 T 0.306 '

    print(motif.matrix_id)

    # Write fixed header
    meme_str = 'MEME version 4' + '\n\n'
    meme_str += 'ALPHABET= ' + ALPHABET + '\n\n'
    meme_str += 'strands: + -' + '\n\n'

    # Write background frequencies
    meme_str += "\n".join(['Background letter frequencies', BFREQ]) + '\n\n'

    # Counts to PWM
    nsites = sum([motif.counts[nt][0] for nt in list(ALPHABET)])
    motif_pwm = motif.counts.normalize()

    # https://biopython.org/docs/1.76/api/Bio.motifs.matrix.html#Bio.motifs.matrix.FrequencyPositionMatrix
    print(motif.counts)    # Bio.motifs.matrix.FrequencyPositionMatrix
    print(motif_pwm)

    # Write matrix header
    meme_str += 'MOTIF %s\n' % motif.matrix_id
    meme_str += 'letter-probability matrix: alength= %i w= %i nsites= %i E= %s\n' % (len(motif_pwm), len(motif_pwm[0]), nsites, "4.1e-009")

    # Iterate motif position
    for i in range(len(motif_pwm[0])):
        # Extract weights for each nt
        tokens = [str(motif_pwm[nt][i]) for nt in list(ALPHABET)]
        # Append the weights to the final string
        meme_str += "\t".join(tokens) + "\n"

    # print(meme_str)
    # raise("MEME format not yet implemented")

    return(meme_str)

# MEME version 4

# ALPHABET= ACGT

# strands: + -

# Background letter frequencies
# A 0.303 C 0.183 G 0.209 T 0.306 

# MOTIF crp
# letter-probability matrix: alength= 4 w= 19 nsites= 17 E= 4.1e-009 
#  0.000000  0.176471  0.000000  0.823529 
#  0.000000  0.058824  0.647059  0.294118 
#  0.000000  0.058824  0.000000  0.941176 
#  0.176471  0.000000  0.764706  0.058824 
#  0.823529  0.058824  0.000000  0.117647 
#  0.294118  0.176471  0.176471  0.352941 
#  0.294118  0.352941  0.235294  0.117647 
#  0.117647  0.235294  0.352941  0.294118 
#  0.529412  0.000000  0.176471  0.294118 
#  0.058824  0.235294  0.588235  0.117647 
#  0.176471  0.235294  0.294118  0.294118 
#  0.000000  0.058824  0.117647  0.823529 
#  0.058824  0.882353  0.000000  0.058824 
#  0.764706  0.000000  0.176471  0.058824 
#  0.058824  0.882353  0.000000  0.058824 
#  0.823529  0.058824  0.058824  0.058824 
#  0.176471  0.411765  0.058824  0.352941 
#  0.411765  0.000000  0.000000  0.588235 
#  0.352941  0.058824  0.000000  0.588235 


# Main program which takes in input parameters
if __name__ == '__main__':

    # Get params
    args = getParams()

    # Get JASPAR db object
    jdb_obj = jaspardb()
    if (args.jdb_version != None):
        jaspardb(release=args.jdb_version)

    # Extract accessions list
    reader = open(args.input, 'r')
    accessions_list = [line.strip().split('\t')[0] for line in reader]
    reader.close()

    # Fetch motifs
    motifs = [jdb_obj.fetch_motif_by_id(a) for a in accessions_list]

    # Write PWMs to files
    for m in motifs:

        # Save motif string
        motif_str = ""
        if (args.format in ['pfm', 'jaspar']):
            pyj.write([m], args.format)
        elif (args.format == 'meme'):
            motif_str = get_meme_formatted_str(m)
        else:
            raise Exception("Unrecognized user-provided PWM format value: %s" % args.format)

        # Write motif string
        writer = open("%s_motif.%s" % (m.matrix_id, args.format), 'w')
        writer.write(motif_str)
        writer.close()


