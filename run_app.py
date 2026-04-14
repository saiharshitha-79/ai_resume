import os
import sys
import streamlit.web.cli as stcli

if __name__ == "__main__":
    if getattr(sys, 'frozen', False):
        app_path = os.path.join(sys._MEIPASS, 'app.py')
    else:
        app_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app.py')
    sys.argv = ["streamlit", "run", app_path, "--global.developmentMode=false"]
    sys.exit(stcli.main())
