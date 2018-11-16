#! /bin/bash
if [ "$#" -ne 1 ]
then
    echo "Usage: $0 inputfile"
    exit 1
fi
chmod +x 111508041_code-2.py
python3 111508041_code-2.py $1
