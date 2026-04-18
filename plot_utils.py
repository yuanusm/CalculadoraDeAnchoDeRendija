import numpy as np


def generar_grafica_con_resumen(L, y_m, y_fit, C, delta_C, intercept, titulo, resumen, path_salida):
    try:
        import matplotlib.pyplot as plt
    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError(
            "matplotlib no está instalado. Instálalo con: pip install matplotlib"
        ) from exc

    L = np.array(L, dtype=float)
    y_m = np.array(y_m, dtype=float)
    y_fit = np.array(y_fit, dtype=float)

    orden = np.argsort(L)
    L_sorted = L[orden]
    y_fit_sorted = y_fit[orden]

    fig = plt.figure(figsize=(11, 5.5), constrained_layout=True)
    gs = fig.add_gridspec(1, 2, width_ratios=[2.1, 1.0])
    ax = fig.add_subplot(gs[0, 0])
    ax_info = fig.add_subplot(gs[0, 1])

    y_fit_sup = (C + delta_C) * L_sorted + intercept
    y_fit_inf = (C - delta_C) * L_sorted + intercept

    ax.plot(L, y_m, "o", color="#1f77b4", label="Datos experimentales")
    ax.plot(L_sorted, y_fit_sorted, "-", color="#d62728", linewidth=2, label=f"Ajuste: C={C:.4g} ± {delta_C:.2g}")
    ax.fill_between(L_sorted, y_fit_inf, y_fit_sup, color="#d62728", alpha=0.18, label="Incertidumbre de pendiente")
    ax.set_title(f"{titulo}\nGráfica y vs L")
    ax.set_xlabel("L (m)")
    ax.set_ylabel("y (m)")
    ax.grid(True, alpha=0.3)
    ax.legend(loc="best")

    ax_info.axis("off")
    ax_info.text(
        0.02,
        0.98,
        "Resumen de resultados\n\n" + resumen,
        va="top",
        ha="left",
        fontsize=10.5,
        family="monospace",
        bbox=dict(boxstyle="round,pad=0.5", facecolor="#f8f8f8", edgecolor="#999999"),
    )

    fig.savefig(path_salida, dpi=180)
    plt.close(fig)
