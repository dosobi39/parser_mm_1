#!/usr/bin/env bash

python3 -m pip install -r requirements.txt
cd m_m

echo ''
echo '[**INFO**] - Run mm_parser'
echo '[**INFO**] - Please wait...'

scrapy crawl mm_parser

echo '[**INFO**] - FINISHED WORK mm_parser'