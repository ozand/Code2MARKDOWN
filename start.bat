@echo on
echo Starting backend and frontend...
cd /d "T:\OneDrive\Code\python\Tools\Code2MARKDOWN\"
call .venv\Scripts\activate.bat
start /min cmd /c "streamlit run app.py"