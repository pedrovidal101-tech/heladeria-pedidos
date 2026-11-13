# Heladería - Sistema de pedidos con asistente de IA

API en Django REST Framework con SQL Server, autenticación JWT, asistente de IA (Ollama) con memoria conversacional y un front web.

## Requisitos
- Python 3.12
- SQL Server (puerto 1434) con la base `HeladeriaDB` (script: `script_base_datos.sql`)
- ODBC Driver 17 for SQL Server
- Ollama con el modelo `llama3.2:3b`

## Instalación
```
pip install -r requirements.txt
ollama pull llama3.2:3b
```

## Configuración
Definir la contraseña de la base de datos como variable de entorno (Windows):
```
set DB_PASSWORD=tu_contraseña
```

## Ejecución
```
cd api-django
python manage.py migrate ia
python manage.py runserver
```
Abrir en el navegador: http://127.0.0.1:8000/chat/

## Qué incluye
- CRUD de productos, mesas y pedidos (`/api/`)
- Login con JWT (`/api/auth/token/`)
- Asistente de IA que lee el menú real desde la base de datos (`/api/ia/asistente/`)
- Memoria conversacional por usuario (`/api/ia/conversaciones/`)
- Front web con login, chat y menú de productos (`/chat/`)

## Nota
Se requiere un usuario creado en Django (`python manage.py createsuperuser`) para iniciar sesión.