@echo off
cd /d "%~dp0.."
python -m pipelines.run_all
pause
