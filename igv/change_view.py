import argparse
import re
import xml.etree.ElementTree as ET

def getParams():
    '''Parse parameters from the command line'''
    parser = argparse.ArgumentParser(description='''
This script will change the genomic locus for a saved IGV session file and save it as a new session.

Example: python change_view.py -i INPUT.xml --locus chrIV:1359619-1360157 -o OUTPUT.xml''')
    parser.add_argument('-i','--input', metavar='igv_session_xml', required=True, help='an XML file of the IGV session to use')
    parser.add_argument('--locus', metavar='chrname:start-stop', default='All', help='standard notation for genomic locus/range (e.g. chrIV:1359619-1360157), resets to "All" if none specified')
    parser.add_argument('-o','--output', metavar='igv_session_xml', required=True, help='an XML file of the updated IGV session')

    args = parser.parse_args()
    return(args)

if __name__ == "__main__":
    '''Append pair of BigWigs as a overlaid track.'''

    # Get params
    args = getParams()

    # Validate locus
    pattern = '[a-zA-Z0-9]+:[0-9]+-[0-9]+'

    # Parse XML
    tree = ET.parse(args.input)
    root = tree.getroot() # Session
    root.set('locus', args.locus)

    # Write final element tree
    tree.write(args.output)