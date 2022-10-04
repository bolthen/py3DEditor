from ui.app_window import MyApp
from pathlib import Path

app_path = Path(__file__).parent

if __name__ == '__main__':
    app = MyApp()
    app.MainLoop()

