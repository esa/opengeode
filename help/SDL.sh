#!/bin/bash

if [ -d "wiki" ]; then
    echo "Wiki folder already exists, updating..."
    git -C wiki pull
else
    echo "Cloning wiki folder..."
    git clone https://gitlab.esa.int/taste/taste-setup.wiki.git wiki
fi

if [ $? -eq 0 ]; then
    ./process_gitlab_wiki.py && \
    mv html_output/opengeode.qch .. && \
    mv html_output/opengeode.qhc ..
else
    echo "Failed to retrieve or update wiki."
    exit 1
fi
