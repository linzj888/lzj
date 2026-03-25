@echo off
cd "C:\Users\sugon\Documents\trae_projects\skilltest\.agents\skills\abaqus-odb-extractor"
"C:\SIMULIA\Commands\abaqus.bat" python "scripts\extract_odb.py" --odb_path "D:\test\parametric_inp_fixed\Tensile_E250000.odb" --variables U --output "D:\test\parametric_inp_fixed\extracted_U_250000.csv"
echo Extraction completed!
pause