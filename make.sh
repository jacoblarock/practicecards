#!/bin/bash

rm -v -rf ../dist/static ../dist/templates  ../build
pyinstaller --distpath ../dist --workpath ../build --onefile --add-data "./static/:static" --add-data "./templates/:templates" ./main.py
cp -v -r ./static ../dist/static
cp -v -r ./templates ../dist/templates
rm main.spec
