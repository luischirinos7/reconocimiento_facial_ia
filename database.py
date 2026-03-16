import sqlite3
import json

# Conexión a la base de datos local
def conectar():
    return sqlite3.connect('sistema_facial.db')

# Crear las tablas obligatorias si no existen
def inicializar_db():
    conn = conectar()
    cursor = conn.cursor()
    
    # Tabla para Registrar Personas (Módulo de Registro)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS personas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            apellido TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            embedding TEXT NOT NULL
        )
    ''')
    
    # Tabla para el Historial de Detecciones Emocionales
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS historial_emociones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            persona_id INTEGER,
            emocion TEXT,
            confianza REAL,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(persona_id) REFERENCES personas(id)
        )
    ''')
    conn.commit()
    conn.close()
    print("Base de datos inicializada correctamente.")

# Función para guardar una nueva persona validando duplicados
def registrar_persona(nombre, apellido, email, embedding):
    conn = conectar()
    cursor = conn.cursor()
    try:
        # Convertimos la lista de números (embedding) a texto para guardarlo
        embedding_str = json.dumps(embedding)
        cursor.execute('INSERT INTO personas (nombre, apellido, email, embedding) VALUES (?, ?, ?, ?)',
                       (nombre, apellido, email, embedding_str))
        conn.commit()
        return True, "Registro exitoso."
    except sqlite3.IntegrityError:
        # Esto valida que no existan duplicados por email
        return False, "Error: El email ya está registrado en el sistema."
    finally:
        conn.close()

# Si ejecutas este archivo solo, crea las tablas
if __name__ == "__main__":
    inicializar_db()