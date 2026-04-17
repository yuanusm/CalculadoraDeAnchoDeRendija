# Calculadora de Ancho de Rendija (Tkinter)

Aplicación de escritorio en Python para estimar el ancho de rendija por difracción de rendija simple.

## Ejecutar en modo script

```bash
python slit_gui.py
```

## Exportar como aplicación final (Windows / Linux)

> Recomendación importante: **compila en el sistema destino**.
> - Para Windows, genera `.exe` en Windows.
> - Para Linux, genera binario en Linux.

### 1) Instalar dependencias

```bash
python -m pip install -r requirements.txt
```

### 2) Compilar

#### Linux

```bash
bash build_linux.sh
```

Salida esperada:
- `dist/CalculadoraRendija`

#### Windows (CMD)

```bat
build_windows.bat
```

Salida esperada:
- `dist\CalculadoraRendija.exe`

## Entrega a otro computador

- Copia el ejecutable generado dentro de `dist/`.
- Si quieres incluir ícono o metadatos, se puede extender el comando de PyInstaller (`--icon`, `--version-file`).

## Notas

- Tkinter suele venir incluido con Python estándar.
- Si en algún entorno falta Tcl/Tk, instala el paquete de Tk de tu distribución/sistema.
