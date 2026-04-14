
### get some sample gff3/gtf files from GENCODE

```sh

BASE_URL=https://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_38/GRCh37_mapping/
GENCODE_FILES=(
    "gencode.v38lift37.annotation.gff3.gz"
    "gencode.v38lift37.annotation.gtf.gz"
    "gencode.v38lift37.basic.annotation.gff3.gz"
    "gencode.v38lift37.basic.annotation.gtf.gz"
)

for file in $GENCODE_FILES;
do
    base=$(basename $file ".gz")
    ext=$(echo ${base##*.} )
    name=$(basename $base $ext)

    curl ${BASE_URL}/$file | gzip -dc | head -n 50 > test/sample_${name}${ext}

done

```