@echo off

rem Compile UMAT subroutine
echo Compiling UMAT subroutine...
abaqus make library=steel_plasticity_failure_umat.f

if %errorlevel% neq 0 (
    echo Compilation failed!
    pause
    exit /b 1
)

echo Compilation successful!

rem Run Abaqus analysis
echo Running Abaqus analysis...
abaqus job=steel_test input=steel_test.inp

if %errorlevel% neq 0 (
    echo Analysis failed!
    pause
    exit /b 1
)

echo Analysis completed successfully!

rem Post-process results
echo Post-processing results...
abaqus python post_process.py

echo All tasks completed!
pause
