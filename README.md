# Command Line Interface for Skribos

## Introduction

Skribos is a document build tool for Markdown based documents

## Requirements

## Skribos.yml anatomy

### Downloads section
Supported download sources in the current version: GitHub

Specify the download with "- github: username/repository". Option "to" will set the target folder. You can set the branch with "branch" and tag with the "tag" option. If the "override" option is set, the local repository will be overridden each time Skribos updates the downloads. Every local change will be lost.

### Chapter section

Chapters are document files which will be provided to Jobs as a single string.

### Build section

In the build section you can specify the jobs which will run shell commands. Also you can define some constants which can be used in the command by prepending the dollar sign.

## Example recipe

```
downloads:
  - github: leonidlezner/skribos-cli-demo-common
    to: external
    override: true
    branch: dev1.3
  - github: leonidlezner/skribos-cli-demo-media
    to: external
    override: true
    tag: v0.5
  - github: leonidlezner/skribos-cli-demo-license
    to: external

chapters:
  - external/skribos-cli-demo-common/cover.md
  - external/skribos-cli-demo-license/license.md
  - dist/book/katas.md
  - dist/book/kata1.md
  - external/skribos-cli-demo-common/back.md

build:
  vars:
    output: build
    base: demo_doc
    language: de-de

  jobs:
    - name: "Create output directory"
      command: mkdir -p $output
    
    - name: "Convert PDF"
      command: pandoc $files -o $output/$base.pdf --from markdown --number-sections -V lang=$language

    - name: "Convert DOCX"
      command: pandoc $files -o $output/$base.docx --from markdown --number-sections -V lang=$language
```

