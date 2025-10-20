##   **Script to Generate PDF of the Course**
## Usage Instructions:
## - Requires `asciidoctor-pdf` to be installed on the system.
## - Place this script in the root directory of your content repository.
## - Run the script using: sh pdfgen.sh
##
## Limitations:
## - This script has been tested only on Linux systems.
## - Images included in the content are not rendered in the generated PDF.
##
## TODO:
## - A better alternative would be to use one of Antora's official npm packages for PDF generation.

count=1
filename=$(basename $(pwd)).pdf
echo -ne "Processing the content repository .  . "

for line in `cat antora.yml | grep adoc | awk '{print $2}'`
do
	dir=`dirname $line`
	asciidoctor-pdf modules/ROOT/pages/index.adoc -o ./file.pdf
	for file in `cat $line | grep xref | sed -E 's/.*xref:([^[]+).*/\1/'`
	do
		echo -ne " . "
		asciidoctor-pdf $dir/pages/$file -o ./file$count.pdf > /dev/null 2>&1
		list="$list file$count.pdf"
		count=$((count+1))
	done
done

echo -ne " . done\n"
pdftk $list cat output $filename
rm -f file*.pdf
echo -e "Look for the file '$filename' generated in the current directory."
