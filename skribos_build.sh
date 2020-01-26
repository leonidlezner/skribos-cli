#!/bin/bash

output=${1-${BUILD_DIR-dist}}
base=$2
language=$3
defaults=${4-'lernos-de'}
pdf_template='external/lernos-common/templates/eisvogel.tex'

function calc_version() {
    long_version=`git describe --tags --long | sed 's/-g[a-z0-9]\{7\}//'`
    branch=`git rev-parse --abbrev-ref HEAD`

    if [ ! $branch = 'master' ]; then
        branch=" ($branch)"
    else
        branch=""
    fi

    export version="${long_version}${branch}"
}

function prepare_target {
    mkdir -p $output
}

function convert_pdf {
    echo "Creating PDF format..."
    pandoc -o $output/$base.pdf -V lang=$language -V date="$version" --template=$pdf_template --defaults $defaults
    
    echo "Creating cover image..."
    convert -density 300 $output/$base.pdf[0] $output/ebook-cover.png
}

function convert_epub {
    echo "Creating EPUB format..."
    pandoc -s -o $output/$base.epub --epub-cover-image=$output/ebook-cover.png -V date="$version" --defaults $defaults
}

function convert_mobi {
    echo "Creating MOBI format..."
    ebook-convert $output/$base.epub $output/$base.mobi
}

function convert_docx {
    echo "Creating DOCX format..."
    pandoc -o $output/$base.docx -V lang=$language -V date="$version" --defaults $defaults
}

function convert_html {
    echo "Creating HTML format..."
    pandoc -o $output/$base.html -V lang=$language -V date="$version" --extract-media ./images --defaults $defaults
    cp -r ./images $output && rm -r ./images
}

calc_version
prepare_target
convert_html
convert_pdf
convert_epub
convert_mobi
convert_docx