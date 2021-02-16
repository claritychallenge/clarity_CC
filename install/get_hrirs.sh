#!/usr/bin/env bash

#TODO: Currently just ED files

INSTALLATION_DIR=$1
mkdir "$INSTALLATION_DIR"/hrir

filekey="1LmJjLBaQTb0ILhQ_IAbo5FuM07OSSpZm"
filename="$INSTALLATION_DIR"/hrir/hrir.tar.gz

# Licence text approved by Florian Denk 22/10/2020
text="The data are published under the terms of the Creative Commons BY-NC-SA 4.0 license.\
You are free to use, transform and redistribute the data for non-commercial purposes, \
provided the original source is attributed and further distribution is made under the same \
license as the original. In addition, you are free to use, transform and redistribute the data for \
the purposes of the public competition 'Clarity round one', provided the original source is \
attributed and further distribution is made under the same license as the original. \
The data were originally published at medi.uni-oldenburg.de/hearingdevicehrtfs. When you use the \
data, please cite the following: F. Denk, S.M.A. Ernst, S.D. Ewert and B. Kollmeier, (2018). \
Adapting hearing devices to the individual ear acoustics: Database and target response correction \ functions for various device styles. Trends in Hearing, vol 22, p. 1-19. DOI:10.1177/2331216518779313."

echo "$text" 


read -r -p "I accept the terms of the license agreement. [Y/N]" response
case "$response" in [yY][eE][sS]|[yY]) 
    wget --save-cookies "$INSTALLATION_DIR"/hrir/cookies.txt 'https://docs.google.com/uc?export=download&id='$filekey'' -O- \
    | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1/p' > "$INSTALLATION_DIR"/hrir/confirm.txt
    wget --load-cookies "$INSTALLATION_DIR"/hrir/cookies.txt -O "$filename" \
        'https://docs.google.com/uc?export=download&id='$filekey'&confirm='$(<"$INSTALLATION_DIR"/hrir/confirm.txt)
    tar -xvf "$filename" --directory "$INSTALLATION_DIR"/hrir
    rm "$filename"
        ;;
    *)
        echo "Licence agreement is required for download."
        ;;
esac


# e.g. source get_hrirs.sh "$INSTALLATION_DIR"





