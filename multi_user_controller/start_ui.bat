
set watertap_ui_path=D:\OneDrive\NAWI_work\Analysis\WaterTAP\watertap-ui\backend\app

call conda activate watertap-ui-env

call cd %watertap_ui_path%
echo -------------------------------------------------
call python main.py
@REM call npm run app-start
@REM call concurrently -k "python ../backend/app/main.py" "react-scripts start"
pause
