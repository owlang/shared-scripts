
MDFILE=auto_README.md

for PYSCRIPT in */*.py;
do
    NAME=`basename $PYSCRIPT`

    echo "### ${NAME}" >> $MDFILE
    echo "" >> $MDFILE


    echo "\`\`\`" >> $MDFILE
    python $PYSCRIPT -h >> $MDFILE
    echo "\`\`\`" >> $MDFILE
    echo "" >> $MDFILE

done

for PLSCRIPT in */*.pl;
do
    NAME=`basename $PLSCRIPT`

    echo "### ${NAME}" >> $MDFILE
    echo "" >> $MDFILE


    echo "\`\`\`" >> $MDFILE
    perl $PLSCRIPT 2>> $MDFILE
    echo "\`\`\`" >> $MDFILE
    echo "" >> $MDFILE

done
