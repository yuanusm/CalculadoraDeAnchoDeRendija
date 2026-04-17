import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
from scipy import stats


# ─────────────────────────── UTILIDADES ───────────────────────────
def sig_figs_round(value, uncertainty):
    if uncertainty == 0 or np.isnan(uncertainty):
        return f"{value:.6g}", f"{uncertainty:.2g}"
    exp = int(np.floor(np.log10(abs(uncertainty))))
    decimals = max(0, -exp + 1)
    return f"{round(value, decimals):.{decimals}f}", f"{round(uncertainty, decimals):.{decimals}f}"


# ─────────────────────────── APP ───────────────────────────
class App:
    MAX_FILAS = 20

    def __init__(self, root):
        self.root = root
        root.title("Difracción - Ancho de Rendija (Single Slit)")
        root.geometry("760x680")
        root.minsize(700, 620)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", rowheight=24)

        container = ttk.Frame(root, padding=8)
        container.pack(fill="both", expand=True)

        # Layout compacto vertical
        top = ttk.Frame(container)
        top.pack(fill="x", pady=(0, 6))

        bottom = ttk.Frame(container)
        bottom.pack(fill="both", expand=True)

        # ====================== PARÁMETROS ======================
        param_frame = ttk.LabelFrame(top, text=" Parámetros del Experimento ", padding=8)
        param_frame.pack(fill="x")

        ttk.Label(param_frame, text="λ (nm):").grid(row=0, column=0, sticky="w", pady=2)
        self.lambda_entry = ttk.Entry(param_frame, width=9)
        self.lambda_entry.grid(row=0, column=1, padx=(4, 12))
        self.lambda_entry.insert(0, "532")

        ttk.Label(param_frame, text="Δλ (nm):").grid(row=0, column=2, sticky="w", pady=2)
        self.dlambda_entry = ttk.Entry(param_frame, width=9)
        self.dlambda_entry.grid(row=0, column=3, padx=(4, 12))
        self.dlambda_entry.insert(0, "10")

        ttk.Label(param_frame, text="m (orden):").grid(row=0, column=4, sticky="w", pady=2)
        self.m_entry = ttk.Entry(param_frame, width=7)
        self.m_entry.grid(row=0, column=5, padx=(4, 10))
        self.m_entry.insert(0, "5")

        self.lateral_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            param_frame,
            text="Modo medición lateral (2m): interpretar y como 2m y usar y/2 internamente",
            variable=self.lateral_var,
        ).grid(row=1, column=0, columnspan=6, sticky="w", pady=(4, 0))

        btn_frame = ttk.Frame(top)
        btn_frame.pack(fill="x", pady=(6, 0))

        ttk.Button(btn_frame, text="Agregar fila", command=self.agregar_fila).pack(side="left", padx=(0, 4))
        ttk.Button(btn_frame, text="Eliminar fila", command=self.eliminar_fila).pack(side="left", padx=4)
        ttk.Button(btn_frame, text="Limpiar tabla", command=self.limpiar_tabla).pack(side="left", padx=4)
        ttk.Button(btn_frame, text="Calcular", command=self.calcular).pack(side="left", padx=4)

        # ====================== ZONA INFERIOR ======================
        left = ttk.Frame(bottom)
        left.pack(side="left", fill="both", expand=True, padx=(0, 6))

        right = ttk.Frame(bottom)
        right.pack(side="right", fill="both", expand=True, padx=(6, 0))

        # ====================== TABLA DE DATOS ======================
        data_frame = ttk.LabelFrame(left, text=" Datos Experimentales  (L en metros  |  y en centímetros) ", padding=8)
        data_frame.pack(fill="both", expand=True)

        self.tree = ttk.Treeview(data_frame, columns=("L", "y"), show="headings", height=self.MAX_FILAS)
        self.tree.heading("L", text="L (m)")
        self.tree.heading("y", text="y (cm)")
        self.tree.column("L", width=180, anchor="center")
        self.tree.column("y", width=180, anchor="center")
        self.tree.pack(fill="both", expand=True)

        self.tree.bind("<ButtonRelease-1>", self.on_click)

        self.entry_edit = None
        self.current_item = None
        self.current_column = None

        # ====================== RESULTADOS ======================
        result_forced = ttk.LabelFrame(right, text=" Resultado: Ajuste forzado por origen ", padding=8)
        result_forced.pack(fill="both", expand=True, pady=(0, 6))
        self.resultado_forzado = tk.Text(result_forced, height=11, font=("Consolas", 10))
        self.resultado_forzado.pack(fill="both", expand=True)

        result_free = ttk.LabelFrame(right, text=" Resultado: Ajuste sin forzar origen ", padding=8)
        result_free.pack(fill="both", expand=True, pady=(0, 6))
        self.resultado_libre = tk.Text(result_free, height=11, font=("Consolas", 10))
        self.resultado_libre.pack(fill="both", expand=True)

        warning_frame = ttk.LabelFrame(right, text=" Advertencias ", padding=8)
        warning_frame.pack(fill="x", pady=(0, 6))
        self.warnings = tk.Text(warning_frame, height=6, font=("Consolas", 10), foreground="#b22222")
        self.warnings.pack(fill="x")

        self._crear_filas_iniciales()

    # ====================== EDICIÓN DIRECTA EN CELDA ======================
    def on_click(self, event):
        region = self.tree.identify("region", event.x, event.y)
        if region != "cell":
            return

        # Si había una celda en edición, guárdala antes de cambiar de celda
        if self.entry_edit and self.current_item is not None:
            self.guardar_edicion()

        column = self.tree.identify_column(event.x)
        item = self.tree.identify_row(event.y)
        if not item or column not in ("#1", "#2"):
            return

        self.current_item = item
        self.current_column = 0 if column == "#1" else 1

        values = self.tree.item(item, "values")
        current_value = values[self.current_column]

        x, y, width, height = self.tree.bbox(item, column)
        self.entry_edit = ttk.Entry(self.tree, justify="center")
        self.entry_edit.place(x=x, y=y, width=width, height=height)
        self.entry_edit.insert(0, current_value)
        self.entry_edit.select_range(0, tk.END)
        self.entry_edit.focus()

        self.entry_edit.bind("<Return>", self.guardar_y_mover)
        self.entry_edit.bind("<FocusOut>", self.guardar_edicion)

    def guardar_y_mover(self, event=None):
        if not self.entry_edit or self.current_item is None:
            return

        item_actual = self.current_item
        col_actual = self.current_column
        guardado = self.guardar_edicion()
        if not guardado:
            return

        hijos = self.tree.get_children()
        if item_actual not in hijos:
            return
        idx = hijos.index(item_actual)

        if col_actual == 0:
            next_item, next_col_id = item_actual, "#2"
        else:
            if idx + 1 >= len(hijos):
                return
            next_item, next_col_id = hijos[idx + 1], "#1"

        bbox = self.tree.bbox(next_item, next_col_id)
        if not bbox:
            return

        x, y, width, height = bbox
        fake_event = type("Event", (), {"x": x + width // 2, "y": y + height // 2})()
        self.on_click(fake_event)

    def guardar_edicion(self, event=None):
        if not self.entry_edit or not self.current_item:
            return True

        new_value = self.entry_edit.get().strip()
        if new_value:
            try:
                _ = float(new_value)
            except ValueError:
                messagebox.showerror("Error", "Ingrese un número válido")
                self.entry_edit.focus()
                return False

        values = list(self.tree.item(self.current_item, "values"))
        values[self.current_column] = new_value
        self.tree.item(self.current_item, values=values)

        self.entry_edit.destroy()
        self.entry_edit = None
        self.current_item = None
        self.current_column = None
        return True

    # ====================== GESTIÓN DE FILAS ======================
    def _crear_filas_iniciales(self):
        for _ in range(self.MAX_FILAS):
            self.agregar_fila()

    def agregar_fila(self):
        if len(self.tree.get_children()) >= self.MAX_FILAS:
            return
        item = self.tree.insert("", "end", values=("", ""))
        idx = len(self.tree.get_children()) - 1
        tag = "par" if idx % 2 == 0 else "impar"
        self.tree.item(item, tags=(tag,))
        self.tree.tag_configure("par", background="#ffffff")
        self.tree.tag_configure("impar", background="#f4f7fb")

    def eliminar_fila(self):
        selected = self.tree.selection()
        if selected:
            self.tree.delete(selected[0])
        else:
            messagebox.showwarning("Atención", "Seleccione una fila para eliminar")

    def limpiar_tabla(self):
        if self.entry_edit:
            self.entry_edit.destroy()
            self.entry_edit = None
            self.current_item = None
            self.current_column = None
        for item in self.tree.get_children():
            self.tree.delete(item)
        self._crear_filas_iniciales()

    def _leer_datos(self):
        L_list = []
        y_list_cm = []
        invalid_rows = []
        for idx, row in enumerate(self.tree.get_children(), start=1):
            vals = self.tree.item(row)["values"]
            L_txt = str(vals[0]).strip()
            y_txt = str(vals[1]).strip()
            if not L_txt and not y_txt:
                continue
            try:
                L_list.append(float(L_txt))
                y_list_cm.append(float(y_txt))
            except ValueError:
                invalid_rows.append(idx)

        if invalid_rows:
            raise ValueError(f"Filas con datos no numéricos: {invalid_rows}")

        return np.array(L_list), np.array(y_list_cm)

    # ====================== CÁLCULO (INTACTO POR CADA MODO) ======================
    def _calcular_modo(self, L, y_m, lambda_nm, delta_lambda_nm, m, forzar):
        lam = lambda_nm * 1e-9
        dlam = delta_lambda_nm * 1e-9
        n = len(L)

        # === Ajuste lineal (mismo código robusto) ===
        if forzar:
            C = np.dot(L, y_m) / np.dot(L, L)
            intercept = 0.0
            y_pred = C * L
            SS_res = np.sum((y_m - y_pred) ** 2)
            df = n - 1
        else:
            L_mean = np.mean(L)
            y_mean = np.mean(y_m)
            SS_xx = np.sum((L - L_mean) ** 2)
            SS_xy = np.sum((L - L_mean) * (y_m - y_mean))
            C = SS_xy / SS_xx
            intercept = y_mean - C * L_mean
            y_pred = C * L + intercept
            SS_res = np.sum((y_m - y_pred) ** 2)
            df = n - 2

        SS_tot = np.sum((y_m - np.mean(y_m)) ** 2)
        r2 = 1.0 - SS_res / SS_tot if SS_tot > 0 else 1.0

        if df >= 1:
            s = np.sqrt(SS_res / df)
            if forzar:
                var_C = s**2 / np.dot(L, L)
            else:
                var_C = s**2 / np.sum((L - np.mean(L))**2)
            se_C = np.sqrt(var_C)
            t_factor = stats.t.ppf(0.975, df)
            delta_C = t_factor * se_C
        else:
            delta_C = np.nan
            t_factor = np.nan

        a = m * lam / C
        rel_lam = dlam / lam
        rel_C = abs(delta_C / C) if (not np.isnan(delta_C) and C != 0) else 0.0
        rel_a = np.sqrt(rel_lam**2 + rel_C**2)
        delta_a = a * rel_a

        a_um = a * 1e6
        da_um = delta_a * 1e6
        sv, su = sig_figs_round(a_um, da_um)

        return {
            "C": C,
            "intercept": intercept,
            "y_pred": y_pred,
            "r2": r2,
            "t_factor": t_factor,
            "rel_lam": rel_lam,
            "rel_C": rel_C,
            "rel_a": rel_a,
            "sv": sv,
            "su": su,
            "a_um": a_um,
            "da_um": da_um,
            "n": n,
        }

    def _formatear_resultado(self, result, forzado):
        texto = f"a = {result['sv']} ± {result['su']} µm\n\n"
        texto += f"a (sin restricción) = {result['a_um']:.12g} µm\n"
        texto += f"Δa (sin restricción) = {result['da_um']:.12g} µm\n\n"
        texto += f"Pendiente C     = {result['C']:.6g}\n"
        if not forzado:
            texto += f"Intercepto      = {result['intercept']:.6f} m\n"
        texto += f"R²              = {result['r2']:.5f}\n\n"
        texto += f"δλ/λ   = {result['rel_lam']*100:.3f} %\n"
        texto += f"δC/C   = {result['rel_C']*100:.3f} %   (t = {result['t_factor']:.2f})\n"
        texto += f"δa/a   = {result['rel_a']*100:.3f} %\n"
        return texto

    def _generar_advertencias(self, L, res_forzado, res_libre):
        warnings = []
        n = len(L)

        if n < 5:
            warnings.append("• Pocos puntos experimentales (<5): la incertidumbre puede subestimarse.")

        if res_forzado["r2"] < 0.98:
            warnings.append(f"• Ajuste forzado con R² bajo ({res_forzado['r2']:.4f}).")

        if res_libre["r2"] < 0.98:
            warnings.append(f"• Ajuste libre con R² bajo ({res_libre['r2']:.4f}).")

        y_span = np.max(np.abs(res_libre["y_pred"])) if len(res_libre["y_pred"]) else 0.0
        if y_span > 0:
            intercept_ratio = abs(res_libre["intercept"]) / y_span
            if intercept_ratio > 0.05:
                warnings.append(
                    f"• Intercepto significativo en ajuste libre: {res_libre['intercept']:.3e} m (>{intercept_ratio*100:.1f}% del rango)."
                )

        if not warnings:
            warnings.append("• Sin advertencias críticas: consistencia estadística aceptable con los criterios configurados.")

        return "\n".join(warnings)

    def calcular(self):
        try:
            lambda_nm = float(self.lambda_entry.get())
            delta_lambda_nm = float(self.dlambda_entry.get())
            m = int(self.m_entry.get())

            L, y_cm = self._leer_datos()
            n = len(L)
            if n < 2:
                messagebox.showerror("Error", "Ingrese al menos 2 puntos válidos")
                return

            # Conversión de unidades solicitada
            y_m = y_cm * 1e-2
            if self.lateral_var.get():
                y_m = y_m / 2.0

            # Ambos casos siempre
            res_forzado = self._calcular_modo(L, y_m, lambda_nm, delta_lambda_nm, m, True)
            res_libre = self._calcular_modo(L, y_m, lambda_nm, delta_lambda_nm, m, False)

            self.resultado_forzado.delete("1.0", tk.END)
            self.resultado_libre.delete("1.0", tk.END)
            self.resultado_forzado.insert(tk.END, self._formatear_resultado(res_forzado, True))
            self.resultado_libre.insert(tk.END, self._formatear_resultado(res_libre, False))

            self.warnings.delete("1.0", tk.END)
            self.warnings.insert(tk.END, self._generar_advertencias(L, res_forzado, res_libre))

        except Exception as e:
            messagebox.showerror("Error", f"Error durante el cálculo:\n{str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
