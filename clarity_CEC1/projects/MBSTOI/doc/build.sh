#!/bin/bash
set -eu

die () { echo "ERROR: $*" >&2; exit 2; }

for cmd in pdoc3; do
    command -v "$cmd" >/dev/null ||
    die "Missing $cmd; \`pip install $cmd\`"
done

DOCROOT="$(pwd)"
BUILDROOT="$DOCROOT/build"

echo
echo 'Building docs'
echo
mkdir -p "$BUILDROOT"
rm -r "$BUILDROOT" 2>/dev/null || true
pushd "$DOCROOT/.." >/dev/null
PYTHONPATH=./clarity pdoc3 --html \
--template-dir "$DOCROOT/clarity_template" \
--output-dir "$BUILDROOT" \
MBSTOI
popd >/dev/null


echo
echo "All good. Docs in: $BUILDROOT"
echo
echo "    file://$BUILDROOT/clarity/index.html"
echo
