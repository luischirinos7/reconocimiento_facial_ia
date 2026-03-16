import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import database

class PantallaReportes:
    def __init__(self, window):
        self.window = window
        self.window.title("Reportes y Estadísticas")
        self.window.geometry("800x600")

        # --- Controles Superiores ---
        frame_botones = tk.Frame(self.window)
        frame_botones.pack(pady=10)

        tk.Button(frame_botones, text="Actualizar Datos", command=self.cargar_datos, bg="gray", fg="white", font=("Arial", 10, "bold")).grid(row=0, column=0, padx=10)
        tk.Button(frame_botones, text="Generar Gráfico General", command=self.graficar_emociones, bg="blue", fg="white", font=("Arial", 10, "bold")).grid(row=0, column=1, padx=10)
        tk.Button(frame_botones, text="Exportar Historial a CSV", command=self.exportar_csv, bg="green", fg="white", font=("Arial", 10, "bold")).grid(row=0, column=2, padx=10)

        # --- Tabla de Historial de Detecciones ---
        frame_tabla = tk.Frame(self.window)
        frame_tabla.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        self.tree = ttk.Treeview(frame_tabla, columns=("Nombre", "Emoción", "Confianza", "Fecha"), show='headings', height=8)
        self.tree.heading("Nombre", text="Nombre Registrado")
        self.tree.heading("Emoción", text="Emoción Detectada")
        self.tree.heading("Confianza", text="Confianza (%)")
        self.tree.heading("Fecha", text="Fecha y Hora")
        self.tree.pack(fill=tk.BOTH, expand=True)

        # --- Contenedor para el Gráfico ---
        self.frame_grafico = tk.Frame(self.window)
        self.frame_grafico.pack(fill=tk.BOTH, expand=True, pady=10)

        # Cargar la tabla al iniciar
        self.cargar_datos()

    def cargar_datos(self):
        # Limpiar tabla actual
        for row in self.tree.get_children():
            self.tree.delete(row)

        conn = database.conectar()
        query = """
            SELECT p.nombre || ' ' || p.apellido, h.emocion, h.confianza, h.fecha 
            FROM historial_emociones h 
            JOIN personas p ON h.persona_id = p.id 
            ORDER BY h.fecha DESC
        """
        cursor = conn.cursor()
        cursor.execute(query)
        
        for fila in cursor.fetchall():
            fila_formateada = (fila[0], fila[1], f"{fila[2]:.1f}", fila[3])
            self.tree.insert("", tk.END, values=fila_formateada)
        conn.close()

    def graficar_emociones(self):
        # Limpiar gráfico anterior si existe
        for widget in self.frame_grafico.winfo_children():
            widget.destroy()

        conn = database.conectar()
        df = pd.read_sql_query("SELECT emocion FROM historial_emociones", conn)
        conn.close()

        if df.empty:
            messagebox.showinfo("Sin datos", "No hay detecciones registradas para graficar.")
            return

        # Contar cuántas veces se detectó cada emoción
        conteo = df['emocion'].value_counts()

        # Crear el gráfico con Matplotlib
        fig, ax = plt.subplots(figsize=(8, 4))
        colores = ['#4CAF50', '#2196F3', '#F44336', '#FFC107', '#9C27B0', '#00BCD4', '#795548']
        conteo.plot(kind='bar', color=colores[:len(conteo)], ax=ax)
        
        ax.set_title("Estadísticas Generales de Emociones", fontsize=14, fontweight='bold')
        ax.set_xlabel("Emociones", fontweight='bold')
        ax.set_ylabel("Cantidad de Detecciones", fontweight='bold')
        plt.xticks(rotation=0)
        plt.tight_layout()

        # Incrustar el gráfico dentro de la ventana de Tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.frame_grafico)
        canvas.draw()
        canvas.get_tk_widget().pack()

    def exportar_csv(self):
        conn = database.conectar()
        query = "SELECT p.nombre, p.apellido, h.emocion, h.confianza, h.fecha FROM historial_emociones h JOIN personas p ON h.persona_id = p.id"
        df = pd.read_sql_query(query, conn)
        conn.close()

        if df.empty:
            messagebox.showwarning("Vacío", "No hay datos para exportar.")
            return

        # Guardar como archivo de Excel/CSV
        nombre_archivo = "reporte_emociones.csv"
        df.to_csv(nombre_archivo, index=False, encoding='utf-8-sig')
        messagebox.showinfo("Exportado", f"Datos exportados exitosamente a '{nombre_archivo}'.")

if __name__ == "__main__":
    root = tk.Tk()
    app = PantallaReportes(root)
    root.mainloop()