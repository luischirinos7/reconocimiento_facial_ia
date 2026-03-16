import tkinter as tk
from tkinter import ttk
import cv2
from PIL import Image, ImageTk
from deepface import DeepFace
import numpy as np
import threading
import json
from scipy.spatial.distance import cosine

import database  # Nuestro modulo de base de datos local

TRADUCCION_EMOCIONES = {
    'happy': 'Felicidad',
    'sad': 'Tristeza',
    'angry': 'Enojo',
    'surprise': 'Sorpresa',
    'neutral': 'Neutral',
    'fear': 'Miedo',
    'disgust': 'Disgusto'
}

class PantallaDeteccion:
    def __init__(self, window):
        self.window = window
        self.window.title("Reconocimiento y Emociones")
        self.window.geometry("800x600")
        
        # --- Controles de la Interfaz ---
        frame_controles = tk.Frame(self.window)
        frame_controles.pack(pady=10)
        
        self.detectando = False
        self.analizando = False
        self.resultado_actual = "Esperando rostro..."
        
        self.btn_iniciar = tk.Button(frame_controles, text="Iniciar Deteccion", command=self.iniciar_deteccion, bg="green", fg="white", font=("Arial", 12, "bold"))
        self.btn_iniciar.grid(row=0, column=0, padx=10)
        
        self.btn_detener = tk.Button(frame_controles, text="Detener Deteccion", command=self.detener_deteccion, bg="red", fg="white", font=("Arial", 12, "bold"), state=tk.DISABLED)
        self.btn_detener.grid(row=0, column=1, padx=10)

        # --- Video en tiempo real ---
        self.label_video = tk.Label(self.window)
        self.label_video.pack(pady=10)
        
        # --- Cargar Base de Datos en Memoria ---
        self.cargar_usuarios()

        # Iniciar cámara
        self.cap = cv2.VideoCapture(0)
        self.actualizar_frame()

    def cargar_usuarios(self):
        """Extrae los embeddings guardados para comparar en tiempo real."""
        self.usuarios_db = []
        conn = database.conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre, apellido, embedding FROM personas")
        filas = cursor.fetchall()
        for fila in filas:
            self.usuarios_db.append({
                "id": fila[0],
                "nombre_completo": f"{fila[1]} {fila[2]}",
                "embedding": np.array(json.loads(fila[3]))
            })
        conn.close()
        print(f"Usuarios cargados en memoria listos para comparar: {len(self.usuarios_db)}")

    def iniciar_deteccion(self):
        self.detectando = True
        self.resultado_actual = "Analizando..."
        self.btn_iniciar.config(state=tk.DISABLED)
        self.btn_detener.config(state=tk.NORMAL)

    def detener_deteccion(self):
        self.detectando = False
        self.resultado_actual = "Deteccion pausada."
        self.btn_iniciar.config(state=tk.NORMAL)
        self.btn_detener.config(state=tk.DISABLED)

    def analizar_frame_background(self, frame_para_analizar):
        """Hilo en segundo plano para no congelar el video."""
        try:
            # 1. Analizar Emociones
            analisis = DeepFace.analyze(frame_para_analizar, actions=['emotion'], enforce_detection=False, silent=True)
            emocion_ingles = analisis[0]['dominant_emotion']
            emocion_espanol = TRADUCCION_EMOCIONES.get(emocion_ingles, emocion_ingles)
            confianza_emocion = analisis[0]['emotion'][emocion_ingles]

            # 2. Extraer embedding del frame actual para identificar
            rep = DeepFace.represent(frame_para_analizar, enforce_detection=False)
            embedding_actual = np.array(rep[0]["embedding"])

            # 3. Comparar con la base de datos usando Distancia Coseno
            identidad = "Persona no registrada"
            id_detectado = None
            distancia_minima = 1.0 # Umbral inicial alto

            for usuario in self.usuarios_db:
                dist_actual = cosine(embedding_actual, usuario["embedding"])
                
                # Umbral de 0.40 para confirmar que es la misma persona
                if dist_actual < 0.40 and dist_actual < distancia_minima:
                    distancia_minima = dist_actual
                    identidad = usuario["nombre_completo"]
                    id_detectado = usuario["id"] # Capturamos el ID de la base de datos

            # Actualizar el texto que se mostrara en pantalla
            self.resultado_actual = f"{identidad} | {emocion_espanol} ({confianza_emocion:.1f}%)"

            # 4. Guardar historial de detecciones emocionales en la BD
            if id_detectado is not None:
                conn = database.conectar()
                cursor = conn.cursor()
                cursor.execute("INSERT INTO historial_emociones (persona_id, emocion, confianza) VALUES (?, ?, ?)",
                               (id_detectado, emocion_espanol, float(confianza_emocion)))
                conn.commit()
                conn.close()
        except Exception as e:
            # Si en este milisegundo no hay una cara clara, ignoramos el error
            pass 
        finally:
            # Liberar el candado para que el siguiente frame pueda ser analizado
            self.analizando = False

    def actualizar_frame(self):
        """Actualiza el video cada 30 milisegundos."""
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.flip(frame, 1)
            frame = cv2.resize(frame, (800, 480)) # Redimensionar para que quepa todo
            
            # Si le dimos a "Iniciar Deteccion", mandamos a analizar
            if self.detectando:
                if not self.analizando:
                    self.analizando = True
                    # Copiamos el frame y lo mandamos al hilo de atrás
                    threading.Thread(target=self.analizar_frame_background, args=(frame.copy(),), daemon=True).start()

                # Dibujar el rectángulo negro y el texto verde sobre el video (Overlay)
                cv2.rectangle(frame, (10, frame.shape[0] - 50), (630, frame.shape[0] - 10), (0, 0, 0), -1)
                cv2.putText(frame, self.resultado_actual, (20, frame.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            # Convertir para Tkinter
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
            img = Image.fromarray(cv2image)
            imgtk = ImageTk.PhotoImage(image=img)
            self.label_video.imgtk = imgtk
            self.label_video.configure(image=imgtk)
        
        self.window.after(30, self.actualizar_frame)

    def cerrar(self):
        self.cap.release()
        self.window.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = PantallaDeteccion(root)
    root.protocol("WM_DELETE_WINDOW", app.cerrar)
    root.mainloop()