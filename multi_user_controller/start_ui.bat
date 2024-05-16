
set watertap_ui_path=D:\OneDrive\NAWI_work\Analysis\WaterTAP\watertap-ui\electron\ui

call conda activate watertap-ui-env

call cd %watertap_ui_path%
echo -------------------------------------------------
call npm run app-start
@REM call concurrently -k "python ../backend/app/main.py" "react-scripts start"
pause
