
## Dependencies
```
conda create -n jaspar-api bioconda::pyjaspar
```

## Test examples

```
python search_Accessions_by_TF-name.py -i testdata/jaspar_tf-names.txt -o testdata/jaspar_tf-names.accessions
python search_Accessions_by_TF-name.py -i testdata/jaspar_tf-names.txt -o testdata/jaspar_tf-names.accessions --all
```

```
python get_Metadata_from_Acessions.py -i testdata/jaspar_accessions.txt -o testdata/jaspar_accessions.metadata
```

```
python get_PWMs_from_Acessions.py -i testdata/jaspar_accessions.txt
# MA0004.1_motif.meme
# MA0140.3_motif.meme
# MA0604.1_motif.meme
# MA0605.3_motif.meme
python get_PWMs_from_Acessions.py -i testdata/jaspar_accessions.txt --format pfm
# MA0004.1_motif.pfm
# MA0140.3_motif.pfm
# MA0604.1_motif.pfm
# MA0605.3_motif.pfm
```


## Handy documentation resources

- [MEME Suite site's page on MEME motif file format](https://meme-suite.org/meme/doc/meme-format.html?man_type=web)
- [MEME Suite site's page on alternative motif formats](https://meme-suite.org/meme/doc/motif_conversion.html)

- [pyJASPAR docs for searching by name](https://pyjaspar.readthedocs.io/en/latest/how_to_use.html#get-motifs-by-tf-name)
- [BioPython docs for JASPAR motif objects](https://biopython.org/docs/1.75/api/Bio.motifs.jaspar.html)
- [BioPython docs for position matrix objects and info](https://biopython.org/docs/1.76/api/Bio.motifs.matrix.html#Bio.motifs.matrix.FrequencyPositionMatrix)
