#!/usr/bin/env sh

MODULES=""
OLD_IFS=$IFS
if [[ -f modules.csv ]]; then
    while IFS=, read -r NAME REPO BRANCH; do
        MODULES="$MODULES,$NAME"
    done < modules.csv
fi
IFS=$OLD_IFS
echo ${MODULES#,}
