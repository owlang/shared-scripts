# hpa-api

Scripts that parse Human Protein Atlas data.

## Downloading full HPA data

You can download all HPA data here: https://www.proteinatlas.org/about/download including full XML download at the bottom (`proteinatlas.xml.gz`).

```sh
# or curl command from command line if no gui browser available
curl https://www.proteinatlas.org/download/proteinatlas.xml.gz > proteinatlas.xml.gz
gzip -d proteinatlas.xml.gz # This file is massive - plan for ~13 GB of space
```

If you're curious about how it is organized, check out the [schema](https://v25.proteinatlas.org/download/proteinatlas.xsd) or look at an example entry on a per-gene basis ([HNF1A](https://www.proteinatlas.org/ENSG00000135100.xml)).

> [!NOTE]
> Download instructions updated as of 06-09-2026. HPA may update their architecture at any point rendering these docs out-of-date.

JSON also provides some of this data, but not the antibody metadata we are usually interested in.

### sample from `.xml`

```sh
TOP_N_ENTRIES=20

nlines=$(grep -n '</entry>' proteinatlas.xml | head -n $TOP_N_ENTRIES | tail -1 | awk 'BEGIN{OFS="";FS=":"}{print $1}')
head -n $nlines proteinatlas.xml > top_${TOP_N_ENTRIES}.xml
tail -n 2 proteinatlas.xml >> top_${TOP_N_ENTRIES}.xml
```

## Scripts

### `hpa_extract-antigen-seq_from_xml.py`

This script assumes local download of full XML database and can run in any number of ways:

```sh
python hpa_extract-antigen-seq_from_xml.py proteinatlas.xml HPA034961 -o test/output-HPA034961.tsv --json test/output-HPA034961.json 
python hpa_extract-antigen-seq_from_xml.py proteinatlas.xml HPA020044 HPA006057 -o test/output-two.tsv --json test/output-two.json
python hpa_extract-antigen-seq_from_xml.py proteinatlas.xml -i test/ids.txt -o test/output-ids.tsv --json test/output-ids.json
python hpa_extract-antigen-seq_from_xml.py proteinatlas.xml --all -o test/output-all.tsv --json test/output-all.json
```
