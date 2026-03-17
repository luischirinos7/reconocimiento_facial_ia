# Sistema de Reconocimiento Facial y Analisis de Emociones 

Este proyecto es un software de visión artificial desarrollado en Python que permite registrar usuarios, reconocerlos en tiempo real a través de una cámara web y analizar sus estados emocionales basándose en las 7 emociones básicas.

## 📋 Requisitos Obligatorios 
- Registro de usuarios con persistencia.
- Extracción de **embeddings** faciales mediante DeepFace.
- Análisis de emociones en tiempo real (Felicidad, Tristeza, Enojo, etc.).
- Módulo de reportes con gráficas estadísticas (Matplotlib).
- Exportación de datos a formato CSV.

## 🛠️ Instalación y Configuración

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/luischirinos7/reconocimiento_facial_ia.git

2. **Crear y activar entorno virtual:**
   ```bash
   python -m venv entorno_facial
   .\entorno_facial\Scripts\activate
3. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
4. **Cómo usar el sistema:**
  
El sistema está dividido en módulos independientes:
  1. database.py: Inicializa la base de datos local.
  2. registro.py: Interfaz para dar de alta nuevos usuarios.
  3. deteccion.py: Motor de reconocimiento facial y emociones en vivo.
  4. reportes.py: Visualización de estadísticas y exportación de datos.

Ejecutarlos en ese orden para el correcto funcionamiento.

---

Para que el `README` tenga sentido, falta generar la lista de librerías. Con el entorno virtual activado, escribe este comando en la terminal:

```powershell
pip freeze > requirements.txt
