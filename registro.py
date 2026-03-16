import tkinter as tk
from tkinter import messagebox
import cv2
from PIL import Image, ImageTk
from deepface import DeepFace
import database
import tempfile
import os

class PantallaRegistro:
    def __init__(self, window):
        self.window = window
        self.window.title("Registro Facial")
        self.window.geometry("800x600")
        
        # --- Formulario de Datos Personales ---
        frame_datos = tk.Frame(self.window)
        frame_datos.pack(pady=10)
        
        tk.Label(frame_datos, text="Nombre:").grid(row=0, column=0, padx=5, pady=5)
        self.entry_nombre = tk.Entry(frame_datos)
        self.entry_nombre.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(frame_datos, text="Apellido:").grid(row=0, column=2, padx=5, pady=5)
        self.entry_apellido = tk.Entry(frame_datos)
        self.entry_apellido.grid(row=0, column=3, padx=5, pady=5)
        
        tk.Label(frame_datos, text="Email:").grid(row=0, column=4, padx=5, pady=5)
        self.entry_email = tk.Entry(frame_datos)
        self.entry_email.grid(row=0, column=5, padx=5, pady=5)

        # --- Vista Previa de la Cámara ---
        self.label_video = tk.Label(self.window)
        self.label_video.pack(pady=10)
        
        # --- Boton de Captura ---
        self.btn_capturar = tk.Button(self.window, text="Capturar y Registrar Rostro", command=self.registrar_usuario, bg="green", fg="white", font=("Arial", 12, "bold"))
        self.btn_capturar.pack(pady=10)

        # Inicializar Cámara
        self.cap = cv2.VideoCapture(0)
        self.actualizar_frame()

    def actualizar_frame(self):
        # Leer el video en tiempo real
        ret, frame = self.cap.read()
        if ret:
            # Voltear como espejo y convertir colores para Tkinter
            frame = cv2.flip(frame, 1)
            frame = cv2.resize(frame, (800, 480))
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
            img = Image.fromarray(cv2image)
            imgtk = ImageTk.PhotoImage(image=img)
            self.label_video.imgtk = imgtk
            self.label_video.configure(image=imgtk)
            self.frame_actual = frame # Guardamos el frame actual para cuando le den al botón
        
        # Repetir este proceso cada 10 milisegundos
        self.window.after(10, self.actualizar_frame)

    def registrar_usuario(self):
        nombre = self.entry_nombre.get().strip()
        apellido = self.entry_apellido.get().strip()
        email = self.entry_email.get().strip()

        # Validar que lleno el formulario
        if not nombre or not apellido or not email:
            messagebox.showwarning("Error", "Por favor complete todos los datos personales.")
            return

        self.btn_capturar.config(text="Procesando rostros...", state=tk.DISABLED)
        self.window.update()

        try:
            # Guardar el frame actual temporalmente para que DeepFace lo analice
            temp_path = os.path.join(tempfile.gettempdir(), "temp_face.jpg")
            cv2.imwrite(temp_path, self.frame_actual)
            representacion = DeepFace.represent(img_path=temp_path, enforce_detection=True)
            embedding = representacion[0]["embedding"]

            # Guardar en nuestra db
            exito, mensaje = database.registrar_persona(nombre, apellido, email, embedding)
            
            if exito:
                messagebox.showinfo("Exito", f"¡{nombre} {apellido} registrado correctamente!")
                # Limpiar formulario
                self.entry_nombre.delete(0, tk.END)
                self.entry_apellido.delete(0, tk.END)
                self.entry_email.delete(0, tk.END)
            else:
                messagebox.showerror("Error de Duplicado", mensaje)

        except ValueError:
            # DeepFace lanza ValueError si la foto sale borrosa o no hay un rostro claro
            messagebox.showerror("Mala Calidad", "No se detecto un rostro claro. Mire fijamente a la cámara con buena luz.")
        except Exception as e:
            messagebox.showerror("Error del Sistema", str(e))
        finally:
            self.btn_capturar.config(text="Capturar y Registrar Rostro", state=tk.NORMAL)

    def cerrar(self):
        self.cap.release()
        self.window.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = PantallaRegistro(root)
    root.protocol("WM_DELETE_WINDOW", app.cerrar)
    root.mainloop()