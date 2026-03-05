#!/usr/bin/env python3
"""
Punto de entrada para la interfaz gráfica
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from ui.main_window import MainWindow

if __name__ == "__main__":
    app = MainWindow()
    app.run()
