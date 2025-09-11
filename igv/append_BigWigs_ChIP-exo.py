import os, argparse
import time
import xml.etree.ElementTree as ET

def getParams():
    '''Parse parameters from the command line'''
    parser = argparse.ArgumentParser(description='''
This script will append a pair of BigWigs to the input IGV session. Note filepaths to data may break if IGV session file is moved around.

Example: python append_BigWigs_ChIP-exo.py -i INPUT.xml -f DATA_forward.bw -r DATA_reverse.bw -o OUTPUT.xml''')
    parser.add_argument('-i','--input', metavar='igv_session_xml', required=True, help='an XML file of the IGV session to use')
    parser.add_argument('-f','--forward', metavar='bw_fn', required=True, help='a BigWig file of the forward strand coverage')
    parser.add_argument('-r','--reverse', metavar='bw_fn', required=True, help='a BigWig file of the reverse strand coverage')
    parser.add_argument('-o','--output', metavar='igv_session_xml', required=True, help='an XML file of the updated IGV session')

    parser.add_argument('--title', metavar='trackname', default='My ChIP-exo', help='displayed name of ChIP-exo track')
    parser.add_argument('--font-size', metavar='size', default=10, type=float, help='font size of display')
    parser.add_argument('--track-height', metavar='size', default=40, type=int, help='track height in IGV (pixels)')

    parser.add_argument('--read2', action='store_true', help='use Read2 settings (Endo cut site for Benzonase ChIP-exo)')

    parser.add_argument('--new-panel', action='store_true', help='add to a new panel (insert at top)')

    args = parser.parse_args()
    return(args)

def checkTag(element, tagname):
    for child in element:
        if (child.tag == tagname):
            return True
    return False

if __name__ == "__main__":
    '''Append pair of BigWigs as a overlaid track.'''

    # Get params
    args = getParams()

    # Set color constants
    F_RGB, R_RGB = "0,0,255", "255,0,0"
    if (args.read2):
        F_RGB, R_RGB = "0,255,255", "255,0,255"

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
    forwardResource = ET.SubElement(resourcesElement, 'Resource')
    reverseResource = ET.SubElement(resourcesElement, 'Resource')

    # Set Resource filepaths and types
    forwardResource.set('path', args.forward)
    reverseResource.set('path', args.reverse)
    forwardResource.set('type', 'bw')
    reverseResource.set('type', 'bw')

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
    mergedTrackElement = ET.SubElement(panelElement, 'Track')
    mergedTrackElement.set('attributeKey', 'Overlay')
    mergedTrackElement.set('autoScale', 'false')
    mergedTrackElement.set('autoscaleGroup', '5') # how should i index this?
    mergedTrackElement.set('clazz', 'org.broad.igv.track.MergedTracks')
    mergedTrackElement.set('height', args.height)
    mergedTrackElement.set('fontSize', args.font_size)
    mergedTrackElement.set('id', 'olivia-igv-session-script-%s' % time.time())
    mergedTrackElement.set('name', args.title)
    mergedTrackElement.set('visible', 'true')

    # Set individual Track elements
    forwardTrackElement = ET.SubElement(mergedTrackElement, 'Track')
    forwardTrackElement.set('altColor', F_RGB)
    forwardTrackElement.set('attributeKey', os.path.basename(args.forward))
    forwardTrackElement.set('autoScale', 'false')
    forwardTrackElement.set('autoscaleGroup', '5') # how should i index this?
    forwardTrackElement.set('color', F_RGB)
    forwardTrackElement.set('fontSize', args.font_size)
    forwardTrackElement.set('id', os.path.abspath(args.forward))
    forwardTrackElement.set('name', os.path.basename(args.forward))
    forwardTrackElement.set('renderer', 'BAR_CHART')
    forwardTrackElement.set('visible', 'true')
    forwardTrackElement.set('windowFunction', 'mean')

    reverseTrackElement = ET.SubElement(mergedTrackElement, 'Track')
    reverseTrackElement.set('altColor', R_RGB)
    reverseTrackElement.set('attributeKey', os.path.basename(args.reverse))
    reverseTrackElement.set('autoScale', 'false')
    reverseTrackElement.set('autoscaleGroup', '5') # how should i index this?
    reverseTrackElement.set('color', R_RGB)
    reverseTrackElement.set('fontSize', args.font_size)
    reverseTrackElement.set('id', os.path.abspath(args.reverse))
    reverseTrackElement.set('name', os.path.basename(args.reverse))
    reverseTrackElement.set('renderer', 'BAR_CHART')
    reverseTrackElement.set('visible', 'true')
    reverseTrackElement.set('windowFunction', 'mean')

    # datarangeElement = ET.SubElement(mergedTrackElement, 'DataRange')
    # datarangeElement.set('baseline', '0.0')
    # datarangeElement.set('drawBaseline', 'true')
    # datarangeElement.set('flipAxis', 'false')
    # datarangeElement.set('maximum', '11.0')
    # datarangeElement.set('minimum', '0.0')
    # datarangeElement.set('type', 'LINEAR')

    # Write final element tree
    tree.write(args.output)