#!/usr/bin/env bash
#
# The Clarity pipeline has a number of prerequisites
# The following should install the on a MacOS system with
# the Homebrew package manager (https://brew.sh/)

brew install sox
brew install wget

## If your 'sed' command does not have the '-r' option then you
## will need to replace it with the gnu-sed
#
# brew install gnu-sed
#
## and Add the following to you path
#
# PATH="/usr/local/opt/gnu-sed/libexec/gnubin:$PATH"

# For compiling and running OpenMHA various libraries are needed

brew install libsndfile
brew install pkgconfig
brew install portaudio
brew install jack

# Jack can also be installed using the installer available here https://jackaudio.org/downloads/


# For further help with OpenMHA installation see the instructions available at the OpenMHA site
# https://github.com/HoerTech-gGmbH/openMHA/blob/master/INSTALLATION.md
#
#
# For further help with installation on mac please see the discussion on the Clarity Google
# group here
# https://mail.google.com/mail/u/0/#search/clarity+mac/FMfcgxwLsdBjvVhTvfkTwVZzgFglHgKr
