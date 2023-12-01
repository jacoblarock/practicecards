#!/bin/bash

pyinstaller --distpath ../dist --workpath ../build --onefile --add-data "./static/:static" --add-data "./templates/:templates" ./main.py
cp -r ./static ../dist/static
cp -r ./templates ../dist/templates
rm main.spec
