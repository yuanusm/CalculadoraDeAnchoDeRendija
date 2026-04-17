#!/usr/bin/env bash
set -euo pipefail

python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

pyinstaller \
  --noconfirm \
  --clean \
  --onefile \
  --windowed \
  --name CalculadoraRendija \
  slit_gui.py

echo "Build finalizado. Ejecutable en: dist/CalculadoraRendija"
