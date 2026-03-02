import os
from time import sleep
from flask import Flask, jsonify, request
import psycopg2
import redis

app = Flask(__name__)

DATABASE_URL = os.getenv('DATABASE_URL')
REDIS_HOST = os.getenv('REDIS_HOST', 'redis')

def wait_for_db(max_retries=20):
    for _ in range(max_retries):
        try:
            conn = psycopg2.connect(DATABASE_URL)
            conn.close()
            return
        except Exception:
            sleep(1)
    raise RuntimeError("DB no respondio, esta muerta.")

def inc_visit():
    r = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)
    r.incr("visits")

def create_db():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            nombre VARCHAR(100),
            correo VARCHAR(100),
            direccion VARCHAR(255),
            telefono BIGINT,
            password VARCHAR(80));
                """)
    
    # Checar si hay seeds, si no hay, insertar algunos
    cur.execute("SELECT COUNT(*) FROM users;")
    count = cur.fetchone()[0]

    #Seed
    if count == 0:
        cur.execute("""
            INSERT INTO users (nombre, correo, direccion, telefono, password)
            VALUES 
                ('Juan Pérez', 'juan.perez@example.com', 'Calle 123', 1234567890, 'password123'),
                ('María López', 'maria.lopez@example.com', 'Avenida 456', 0987654321, 'password456');
        """)

    conn.commit()
    conn.close()

@app.get("/")
def home():
    inc_visit()
    return jsonify({"message": "Hola desde Flask!",
                    "services": {
                        "/health": "Verifica la salud de la aplicación",
                        "/visits": "Cuenta las visitas usando Redis (Cuando se accede a / o /users, se incrementa el contador)",
                        "/users": "GET para obtener usuarios, POST para crear un nuevo usuario"
                    }})

@app.get("/health") #Debe comprobar PostgreSQL y Redis
def health():
    try:
        # Verificar conexión a PostgreSQL
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute("SELECT NOW();")
        now = cur.fetchone()[0]
        cur.close()
        conn.close()

        # Verificar conexión a Redis
        r = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)
        pong = r.ping()

        return jsonify({"status": "ok", 
                        "db_time": str(now), 
                        "redis_ping": "pong"})
    
    except Exception as e:
        return jsonify({"status": "error", 
                        "message": str(e)
                        }), 500

#Obtener todos los usuarios
@app.get("/users")
def get_users():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute("SELECT nombre, correo, direccion, telefono FROM users;")
        rows = cur.fetchall()
        conn.close()
        users = [
            {"nombre": r[0], "correo": r[1], "direccion": r[2], "telefono": r[3]}
            for r in rows
        ]
        inc_visit()
        return jsonify({"users": users}), 200
    
    except Exception as e:
        return jsonify({"status": "error", 
                        "message": str(e)
                        }), 500

#Crear un usuario
@app.post("/users")
def create_user():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # Validar que el JSON tenga los campos necesarios y que no estén vacíos
        data = request.get_json()
        required_fields = ['nombre', 'correo', 'direccion', 'telefono', 'password']

        for field in required_fields:
            # Validar que el campo exista en el JSON
            if field not in data:
                return jsonify({"status": "error", 
                                "message": f"Falta el campo '{field}' en el JSON"
                                }), 400
            
            # Validar que el campo no esté vacío
            if data[field] is None or (isinstance(data[field], str) and data[field].strip() == ""):
                return jsonify({"status": "error", 
                                "message": f"El campo '{field}' no puede estar vacío"
                                }), 400
            
            # Validar el formato de los campos
            if field == 'telefono':
                try:
                    int(data[field])
                except ValueError:
                    return jsonify({"status": "error", 
                                    "message": f"El campo '{field}' debe ser un número entero"
                                    }), 400
            
            else:
                if not isinstance(data[field], str):
                    return jsonify({"status": "error", 
                                    "message": f"El campo '{field}' debe ser una cadena de texto"
                                    }), 400
            
            
        nombre = data['nombre']
        correo = data['correo']
        direccion = data['direccion']
        telefono = int(data['telefono'])
        password = data['password']

        cur.execute("""
            INSERT INTO users (nombre, correo, direccion, telefono, password)
            VALUES (%s, %s, %s, %s, %s)
        """, (nombre, correo, direccion, telefono, password))
        conn.commit()

        cur.close()
        conn.close()

        inc_visit()
        return jsonify({"status": "success", "message": "Usuario creado exitosamente", "usuario": {"nombre": nombre, "correo": correo, "direccion": direccion, "telefono": telefono}}), 201
    
    except Exception as e:
        return jsonify({"status": "error", 
                        "message": str(e)
                        }), 500
    

# Solo muestra número de visitas, no incrementa
@app.get("/visits")
def visits():
    try:
        r = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)
        count = r.get("visits")
        return jsonify({
            "visits": int(count) if count is not None else 0
        })
    except Exception as e:
        return jsonify({"status": "error", 
                        "message": str(e)
                        }), 500


if __name__ == "__main__":
    wait_for_db()
    create_db()
    app.run(host="0.0.0.0", port=8000)