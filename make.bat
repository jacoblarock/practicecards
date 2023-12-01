pyinstaller --distpath ../dist --workpath ../build --onefile --add-data "./static/:static" --add-data "./templates/:templates" ./main.py
xcopy static ..\dist\static\
xcopy templates ..\dist\templates\
del main.spec
