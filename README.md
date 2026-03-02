# demo-docker-compose

Aplicación de ejemplo con arquitectura de microservicios usando Docker Compose. Incluye una API REST en Flask, una base de datos PostgreSQL y una caché en Redis.

## Información

Creado por: José Luis Álvarez Mánica
Creado el: 2 de marzo del 2026
Materia: Sistemas distribuidos

---

## Arquitectura

```
┌─────────────────────────────────────────────────┐
│                  Docker Compose                  │
│                                                  │
│  ┌──────────────┐        ┌────────────────────┐  │
│  │   api (Flask)│◄──────►│  db (PostgreSQL 14)│  │
│  │   Puerto 8000│        │   Puerto 5432       │  │
│  └──────┬───────┘        └────────────────────┘  │
│         │                                        │
│         │               ┌────────────────────┐   │
│         └──────────────►│   redis (Redis 7)  │   │
│                         │   Puerto 6379       │   │
│                         └────────────────────┘   │
└─────────────────────────────────────────────────┘
```

| Servicio | Imagen          | Descripción                                 |
|----------|-----------------|---------------------------------------------|
| `api`    | Python 3.11     | API REST en Flask, expuesta en el puerto 8000 |
| `db`     | postgres:14     | Base de datos relacional PostgreSQL         |
| `redis`  | redis:7         | Caché en memoria para conteo de visitas     |

### Endpoints disponibles

| Método | Ruta       | Descripción                              |
|--------|------------|------------------------------------------|
| GET    | `/`        | Bienvenida y listado de servicios        |
| GET    | `/health`  | Estado de conexión a PostgreSQL y Redis  |
| GET    | `/users`   | Lista todos los usuarios                 |
| POST   | `/users`   | Crea un nuevo usuario                    |
| GET    | `/visits`  | Número total de visitas registradas      |

---

## Configuración del entorno (.env)

Crea un archivo `.env` en la raíz del proyecto con las siguientes variables:

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_DB=db_demo
```

> El archivo `.env` es leído automáticamente por Docker Compose.

---

## Levantar el proyecto

### Primera vez (construir imágenes y levantar)

```bash
docker compose up --build
```

### Levantar en segundo plano

```bash
docker compose up --build -d
```

### Detener los contenedores

```bash
docker compose down
```

### Detener y eliminar volúmenes (resetea la base de datos)

```bash
docker compose down -v
```

### Ver logs en tiempo real

```bash
docker compose logs -f
```

### Ver logs de un servicio específico

```bash
docker compose logs -f api
```

---

## Estructura del proyecto

```
demo-docker-compose/
├── docker-compose.yml
├── .env                  # La debe de crear el usuario
├── README.md
├── .gitignore
└── app/
    ├── Dockerfile
    ├── main.py
    └── requirements.txt
```
