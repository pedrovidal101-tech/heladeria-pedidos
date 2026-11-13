from config.settings import *

# Base temporal en memoria, solo para las pruebas
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# Que Django cree las tablas de pedidos en la base temporal
MIGRATION_MODULES = {"pedidos": None}