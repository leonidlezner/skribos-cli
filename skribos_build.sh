#!/bin/bash

output=${1-${BUILD_DIR-dist}}
base=$2
language=$3
defaults=${4-'lernos-de'}
pdf_template='external/lernos-common/templates/eisvogel.tex'

function prepare_target {
    mkdir -p $output
}

function convert_pdf {
    pandoc -o $output/$base.pdf -V lang=$language --template=$pdf_template --defaults $defaults
    convert -density 300 $output/$base.pdf[0] $output/ebook-cover.png
}

function convert_epub {
    pandoc -s -o $output/$base.epub --epub-cover-image=$output/ebook-cover.png --defaults $defaults
}

function convert_mobi {
    ebook-convert $output/$base.epub $output/$base.mobi
}

function convert_docx {
    pandoc -o $output/$base.docx -V lang=$language --defaults $defaults
}

function convert_html {
    pandoc -o $output/$base.html -V lang=$language --extract-media ./images --defaults $defaults
    cp -r ./images $output && rm -r ./images
}

prepare_target
convert_html
convert_pdf
convert_epub
convert_mobi
convert_docx