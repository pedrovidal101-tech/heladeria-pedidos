# Heladería - Sistema de pedidos con asistente de IA

API en Django REST Framework con SQL Server, autenticación JWT, asistente de IA (Ollama) con memoria conversacional y un front web para el mesero y la cocina.

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
Abrir en el navegador: http://127.0.0.1:8000/chat/ e iniciar sesión.

## Pantallas web
- `/chat/`: login, chat con el asistente y menú de productos.
- `/mesero/`: el mesero elige la mesa, agrega productos o dicta el pedido a la IA y lo envía a cocina.
- `/cocina/`: la cocina ve los pedidos pendientes, los pasa a "en preparación" y los despacha.

## Flujo del pedido
1. El mesero escribe, por ejemplo, "2 de vainilla y un brownie" y presiona **Armar con IA**.
2. La IA interpreta el texto y devuelve la lista de productos. La IA nunca escribe en la base de datos.
3. El mesero revisa el pedido y presiona **Enviar a cocina**. Django valida los productos y guarda el pedido.
4. La cocina lo ve en `/cocina/`, presiona **En preparación** y luego **Despachar**.

## Qué incluye
- CRUD de productos, mesas y pedidos (`/api/`)
- Login con JWT (`/api/auth/token/`)
- Asistente de IA que lee el menú real desde la base de datos (`/api/ia/asistente/`)
- Interpretación de pedidos dictados (`/api/ia/asistente/pedido/`)
- Memoria conversacional por usuario (`/api/ia/conversaciones/`)
- Pantallas web de chat, mesero y cocina

## Nota
Se requiere un usuario creado en Django (`python manage.py createsuperuser`) para iniciar sesión.