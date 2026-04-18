import csv
from pathlib import Path


def crear_directorio_exportacion(base_dir=None):
    root = Path(base_dir) if base_dir else Path.cwd()
    carpeta_principal = root / "Calculos_Guardados"
    carpeta_principal.mkdir(parents=True, exist_ok=True)

    idx = 1
    while True:
        carpeta = carpeta_principal / f"Datos_{idx}"
        if not carpeta.exists():
            carpeta.mkdir(parents=True, exist_ok=False)
            return carpeta
        idx += 1


def guardar_archivos_exportacion(
    carpeta,
    L,
    y_cm,
    parametros,
    resultado_forzado,
    resultado_libre,
    advertencias,
    log,
):
    carpeta = Path(carpeta)

    with open(carpeta / "datos.csv", "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["L_m", "y_cm"])
        for l_val, y_val in zip(L, y_cm):
            writer.writerow([f"{l_val:.12g}", f"{y_val:.12g}"])

    with open(carpeta / "resultados.txt", "w", encoding="utf-8") as f:
        f.write("=== Parámetros ===\n")
        for key, value in parametros.items():
            f.write(f"{key}: {value}\n")
        f.write("\n=== Resultado (forzado al origen) ===\n")
        f.write(resultado_forzado)
        f.write("\n=== Resultado (sin forzar origen) ===\n")
        f.write(resultado_libre)
        f.write("\n=== Advertencias ===\n")
        f.write(advertencias)

    with open(carpeta / "log.txt", "w", encoding="utf-8") as f:
        f.write(log)
