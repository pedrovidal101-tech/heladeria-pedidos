from pathlib import Path
from urllib.parse import urlparse

import chromadb
import requests
from django.conf import settings

from pedidos.models import Producto

MODELO_EMBEDDINGS = "nomic-embed-text-v2-moe"
COLECCION = "productos"

# Palabras clave por categoría: ayudan a que "algo frío y dulce" encuentre helados.
PISTAS = {
    "Helados": "postre frío dulce cremoso helado",
    "Postres": "postre dulce caliente chocolate para compartir",
    "Bebidas": "bebida fría dulce batida refrescante",
}


def _url_embed():
    u = urlparse(settings.OLLAMA_CONFIG["URL"])
    return f"{u.scheme}://{u.netloc}/api/embed"


def generar_embeddings(textos):
    """Convierte textos en vectores usando Ollama."""
    if not textos:
        return []
    try:
        r = requests.post(
            _url_embed(),
            json={"model": MODELO_EMBEDDINGS, "input": textos},
            timeout=settings.OLLAMA_CONFIG["TIMEOUT"],
        )
        r.raise_for_status()
        vectores = r.json().get("embeddings")
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"No se pudo generar embeddings: {e}")
    if not vectores or len(vectores) != len(textos):
        raise RuntimeError("Ollama no devolvió todos los embeddings.")
    return vectores


def obtener_coleccion():
    """Abre (o crea) la colección de vectores en ChromaDB."""
    ruta = Path(settings.BASE_DIR) / "data" / "chroma"
    cliente = chromadb.PersistentClient(path=str(ruta))
    return cliente.get_or_create_collection(
        name=COLECCION, metadata={"hnsw:space": "cosine"}
    )


def construir_texto(p):
    pista = PISTAS.get(p.categoria, "")
    return f"{p.nombre}. Categoría: {p.categoria}. {pista}"


def indexar_productos():
    """Guarda en ChromaDB los vectores de los productos disponibles."""
    productos = list(
        Producto.objects.filter(disponible=True).order_by("id_producto")
    )
    if not productos:
        return 0
    coleccion = obtener_coleccion()
    textos = [construir_texto(p) for p in productos]
    vectores = generar_embeddings(textos)
    coleccion.upsert(
        ids=[str(p.id_producto) for p in productos],
        embeddings=vectores,
        documents=textos,
        metadatas=[
            {"nombre": p.nombre, "categoria": p.categoria} for p in productos
        ],
    )
    return len(productos)


def buscar_productos(pregunta, cantidad=3):
    """Busca productos por significado. La disponibilidad se lee de SQL Server."""
    if not pregunta or not pregunta.strip():
        raise ValueError("Debes escribir qué buscas.")
    coleccion = obtener_coleccion()
    total = coleccion.count() or (indexar_productos() and coleccion.count())
    if total == 0:
        return []
    vector = generar_embeddings([pregunta])[0]
    res = coleccion.query(
        query_embeddings=[vector], n_results=min(cantidad, total)
    )
    ids = res.get("ids", [[]])[0]
    por_id = {
        str(p.id_producto): p
        for p in Producto.objects.filter(
            id_producto__in=[int(i) for i in ids], disponible=True
        )
    }
    return [por_id[i] for i in ids if i in por_id]