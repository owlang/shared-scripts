import os, argparse
import time
import xml.etree.ElementTree as ET

def getParams():
    '''Parse parameters from the command line'''
    parser = argparse.ArgumentParser(description='''
This script will append a BED track to the input IGV session. Note filepaths to data may break if IGV session file is moved around.

Example: python append_BED.py -i INPUT.xml -b DATA_forward.bed -o OUTPUT.xml''')
    parser.add_argument('-i','--input', metavar='igv_session_xml', required=True, help='an XML file of the IGV session to use')
    parser.add_argument('-b','--bed', metavar='bed_fn', required=True, help='a BED file to append to track session')
    parser.add_argument('-o','--output', metavar='igv_session_xml', required=True, help='an XML file of the updated IGV session')

    parser.add_argument('--title', metavar='trackname', default='My BED', help='displayed name of BED track')
    parser.add_argument('--font-size', metavar='size', default=10, type=float, help='font size of display')
    parser.add_argument('--track-height', metavar='size', default=40, type=int, help='track height in IGV (pixels)')
    parser.add_argument('--color', metavar='trackname', default='FFFFFF', help='Hexcode for color (default=FFFFFF)')

    # parser.add_argument('--new-panel', action='store_true', help='add to a new panel (insert at top)')

    args = parser.parse_args()
    return(args)


def hexcodeToRGBstring(hexcode):
    # TODO: Implement function
    return("0,255,51")


if __name__ == "__main__":
    '''Append BED track.'''

    # Get params
    args = getParams()


    # Parse XML
    tree = ET.parse(args.input)
    root = tree.getroot() # Session

    # <Resources>
        # <Resource path="../hide/Tracks/PEGR_BIGWIG/12275_Sua7_i5006_BY4741_-_YPD_WT_XO_READ1_forward.bw" type="bw"/>
        # <Resource path="../hide/Tracks/PEGR_BIGWIG/12275_Sua7_i5006_BY4741_-_YPD_WT_XO_READ1_reverse.bw" type="bw"/>
    # </Resources>

    # Get resource (create new if one does not exist)
    resourcesElement = root.find('Resources')
    if (resourcesElement==None):
        resourcesElement = ET.SubElement(root, 'Resources')

    # Add data to resource element
    bedResource = ET.SubElement(resourcesElement, 'Resource')
    bedResource.set('path', args.bed)
    bedResource.set('type', 'bed')

    # <Track attributeKey="Overlay" autoScale="false" autoscaleGroup="5" clazz="org.broad.igv.track.MergedTracks" fontSize="10" id="c4f72b33-eea7-40e7-9cae-f4c91835be1d" name="Sua7-XO" visible="true">
    #     <Track altColor="102,0,255" attributeKey="12275_Sua7_i5006_BY4741_-_YPD_WT_XO_READ1_forward.bw" autoScale="false" autoscaleGroup="5" color="102,0,255" fontSize="10" id="/Users/owl8/Documents/GitHub/2024-Lang_TSS-project/hide/Tracks/PEGR_BIGWIG/12275_Sua7_i5006_BY4741_-_YPD_WT_XO_READ1_forward.bw" name="12275_Sua7_i5006_BY4741_-_YPD_WT_XO_READ1_forward.bw" renderer="BAR_CHART" visible="true" windowFunction="mean"/>
    #     <Track altColor="255,0,255" attributeKey="12275_Sua7_i5006_BY4741_-_YPD_WT_XO_READ1_reverse.bw" autoScale="false" autoscaleGroup="5" color="255,0,255" fontSize="10" id="/Users/owl8/Documents/GitHub/2024-Lang_TSS-project/hide/Tracks/PEGR_BIGWIG/12275_Sua7_i5006_BY4741_-_YPD_WT_XO_READ1_reverse.bw" name="12275_Sua7_i5006_BY4741_-_YPD_WT_XO_READ1_reverse.bw" renderer="BAR_CHART" visible="true" windowFunction="mean"/>
    #     <DataRange baseline="0.0" drawBaseline="true" flipAxis="false" maximum="11.0" minimum="0.0" type="LINEAR"/>
    # </Track>

    # Add to first Panel if none specified
    panelElement = root.find('Panel')
    if (args.new_panel):
        panelElement = ET.Element('Panel')
        root.insert(0, panelElement) # TODO: update to insert at user-specified position

    # Set merged Track element
    trackElement = ET.SubElement(panelElement, 'Track')

    # Set color from hexcode
    RGB = hexcodeToRGBstring(args.color)

    if args.title:
        title = args.title
    else:
        title = os.path.basename(args.bedfile)

    trackElement.set('attributeKey', os.path.basename(args.bedfile))
    trackElement.set('clazz', 'org.broad.igv.track.FeatureTrack')
    trackElement.set('color', RGB)
    trackElement.set('colorScale', 'ContinuousColorScale;0.0;11.0;255,255,255;0,0,178')
    trackElement.set('fontSize', args.font_size)
    trackElement.set('groupByStrand', 'false')
    trackElement.set('height', args.height)
    trackElement.set('id', os.path.abspath(args.bedfile))
    # trackElement.set('id', 'olivia-igv-session-script-%s' % time.time())
    trackElement.set('name', title)
    trackElement.set('visible', 'true')

    # TODO: expanded/squished etc...
    # trackElement.set('', '')

    # Write final element tree
    tree.write(args.output)
