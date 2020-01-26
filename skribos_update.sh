#!/bin/bash

function update_repo() {
    url=$1
    branch=${2-master}
    re="\/([A-Za-z0-9-]+)\.git"
    if [[ $url =~ $re ]]; then 
        repo=${BASH_REMATCH[1]}
        folder="external/$repo"
        if [ -d "$folder" ]; then
            echo "Updating: $folder @$branch"
            git -C $folder checkout $branch
            git -C $folder pull origin $branch
        else
            git clone $url $folder
            git -C $folder checkout $branch
        fi
    fi
}

filename=${1-"external.txt"}

while read -r line || [ -n "$line" ]; do
    update_repo $line
done < $filename