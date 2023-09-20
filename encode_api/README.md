# ENCODE API scripts

These include basic scripts for pulling ENCODE data from the API.

### Handy links:
- [REST API examples](https://www.encodeproject.org/help/rest-api/)
- [Data model](https://www.encodeproject.org/help/data-organization/s)

### Dependencies
```
conda create -n encode-api -c conda-forge requests
```

## Downloading ENCFFXXXXXX
Recall that the href is always structured:
`wget /files/ENCFFXXXXXX/@@download/ENCFFXXXXXX.EXT`

where `EXT` can be `bam`, `fastq.gz`, etc depending on the file type.

## get_BAM_from_ENCODEsearch.py
Get BAM accessions and metadata from an ENCODE search url.

`python get_BAM_from_ENCODEsearch.py -i "https://www.encodeproject.org/search/?type=File&file_format=bam&assembly=hg19&frame=object&biosample_ontology.term_name=K562&format=json&limit=10" -o testdata/bamFromEncodeSearch.tab`

ENCODE search --> BAM + metadata.
- accession
- md5sum
- assembly
- mapped_run_type
- FQ1 (parse "derived_from" files)
- FQ2 (parse "derived_from" files)
- mapped_read_length
- output_category
- output_type
- platform (parse "derived_from" files)
- ENCSR
- biological_replicate
- strain
- assay_title
- target
- technical_replicate
- date_created
- file_size

## get_ENCSR_from_ENCODEsearch.py
Get ENCSR accessions and metadata from an ENCODE search url.

`python get_ENCSR_from_ENCODEsearch.py -i "https://www.encodeproject.org/search/?type=Experiment&control_type%21=%2A&status=released&assay_title=TF+ChIP-seq&assay_title=Histone+ChIP-seq&biosample_ontology.term_name=K562&assembly=GRCh38&perturbed=false&format=json&limit=10" -o testdata/ENCSRXXXXXXFromEncodeSearch.tab`

ENCODE search --> ENCSR + metadata.
- accession
- assay_title
- target_name
- target
- description
- strain
- biosample_summary


## get_ENCFF-Peak_from_ENCODEsearch.py
Get ENCFF (peak) accessions and metadata from an ENCODE search url.

ENCODE search --> ENCFF (peak) + metadata


## get_ENCFF-FQ_from_ENCFF-BAM.py
Get ENCFF (fastq) accessions and metadata from a list of ENCFF (bam) accessions.

ENCFF (bam) --> ENCFF (fastq) + metadata.

## TODO
It may be handy to add these scripts in the future since the ENCODE search results don't always show all the info you want from the downloaded TSV.

ENCSR --> FASTQ info  + metadata

ENCSR --> BAM info  + metadata


## JSON URL examples:
Here is a collection of handy urls as examples for different kinds of payloads in https://jsonformatter.org/json-viewer.

### File objects

#### single-ended (TF ChIP-seq)
- Experiment - https://www.encodeproject.org/experiments/ENCSR000BGW/?format=json
- FASTQ - https://www.encodeproject.org/files/ENCFF000QED/?format=json
- BAM 'alignment' - https://www.encodeproject.org/files/ENCFF671SGF/?format=json
- BAM 'unfiltered alignment' - https://www.encodeproject.org/files/ENCFF994DIZ/?format=json

#### paired-ended (GM DNase-seq)
- Experiment - https://www.encodeproject.org/experiments/ENCSR324UCN/?format=json
- PE FASTQ1 - https://www.encodeproject.org/files/ENCFF879FHU/?format=json
- PE FASTQ2 - https://www.encodeproject.org/files/ENCFF466SUX/?format=json
- PE BAM 'alignment' - https://www.encodeproject.org/files/ENCFF972XRU/?format=json
- PE BAM 'unfiltered alignment' - https://www.encodeproject.org/files/ENCFF924RBT/?format=json

### Experiment objects
