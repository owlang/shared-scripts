# Utilities to build IGV XML

## Example

Starting with blank `sacCer3`and `hg19` IGV session files in `xmldata/`, you can build out your IGV session in the command line before you even open IGV to view it.

```
python change_view.py -i xmldata/igv_session_sacCer3.xml -o zoom.xml --locus "chrI:5000-10000"
python append_BigWigs_ChIP-exo.py -i zoom.xml -f /path/to/forward.bw -r /path/to/reverse.bw -o zoom_with-XO.xml
python append_BED_annotations.py -i zoom_with-XO.xml -b /path/to/NFR_positions.bed -o zoom_with-XO_with-NFR.xml
```

...then load it up into IGV!

<!--Put screenshot here-->

These XML files can then be used to take bulk high-resolution or vectorized browser shots using many open source IGV tools on the internet.


## Development

### XML parser for IGV sessions

https://docs.python.org/3/library/xml.etree.elementtree.html

### API discussion

Consider refactoring these into a more formal API for building IGV-session styled XMLs


## Scripts

### change_view.py (untested)

### append_BigWigs_ChIP-exo.py (untested)

### append_BED_annotations.py (untested)

