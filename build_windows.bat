@echo off
setlocal

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

pyinstaller ^
  --noconfirm ^
  --clean ^
  --onefile ^
  --windowed ^
  --name CalculadoraRendija ^
  slit_gui.py

echo Build finalizado. Ejecutable en: dist\CalculadoraRendija.exe
endlocal
