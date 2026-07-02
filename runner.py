import sys
import os
import threading
import time
import webbrowser
from pathlib import Path
from streamlit.web import cli as stcli

def open_browser():
    # Abre o navegador após o servidor iniciar
    time.sleep(2)
    webbrowser.open("http://localhost:8501")

def main():
    # Corrige o problema de assets quando empacotado com PyInstaller
    if getattr(sys, 'frozen', False):
        bundle_dir = sys._MEIPASS
        os.environ["STREAMLIT_STATIC_DIR"] = os.path.join(bundle_dir, "streamlit", "static")
        os.environ["STREAMLIT_CONFIG_DIR"] = bundle_dir

    # Abre o navegador em thread separada
    threading.Thread(target=open_browser).start()

    # Executa o Streamlit
    app_path = str(Path(__file__).parent / "app.py")
    sys.argv = ["streamlit", "run", app_path, "--server.headless", "true", "--server.port", "8501"]
    sys.exit(stcli.main())

if __name__ == "__main__":
    main()
