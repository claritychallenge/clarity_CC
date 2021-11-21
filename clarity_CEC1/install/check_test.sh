#!/usr/bin/env bash
#

rootdir=$1  # Root direct for relative file names in the manifest
manifest=$2  # Manifest file contain the wav data md5 checksums

while IFS= read -r line
do
    chksum=$(echo $line | cut -d' ' -f 1)
    filenm=$(echo $line | cut -d' ' -f 3)
    newchksum=$(sox $rootdir/$filenm -V0 -t wav - | md5sum | cut -d' ' -f 1)
    if [ $chksum != $newchksum ]; then
        echo "Check FAILED for $filenm"
    fi
done < "$manifest"
