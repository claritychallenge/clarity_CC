#!/usr/bin/env bash
#
# The Clarity pipeline has a number of prerequisites
# The following should install these on an Ubuntu linux system
#

sudo -n true  >& /dev/null
test $? -eq 0 || { echo "You require sudo privilege to run this script"; exit 1; }


echo Installing pre-requisites
while read -r p ; do sudo apt-get install -y $p ; done < <(cat << "EOF"
    libsndfile1-dev
    libasound-dev
    portaudio19-dev
    libportaudio2
    libportaudiocpp0
    ffmpeg
    libav-tools
    python3-venv
    sox
EOF
)
