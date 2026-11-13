import requests
from django.conf import settings
from pedidos.models import Producto


class ErrorIA(Exception):
    pass


def construir_menu():
    lineas = []
    for p in Producto.objects.all():
        nombre = getattr(p, "nombre", str(p))
        categoria = getattr(p, "categoria", "")
        precio = getattr(p, "precio", "")
        disponible = getattr(p, "disponible", True)
        estado = "disponible" if disponible else "AGOTADO"
        lineas.append(f"- {nombre} ({categoria}) | ${precio} | {estado}")
    return "\n".join(lineas) if lineas else "No hay productos registrados."


def consultar_asistente(pregunta, historial=None):
    """
    historial: lista de mensajes anteriores, cada uno como
    {"role": "user" o "assistant", "content": "texto"}
    """
    cfg = settings.OLLAMA_CONFIG
    sistema = (
        "Eres el asistente de una heladería. Responde en español, corto y amable. "
        "Usa SOLO los productos de este menú. Si un producto está AGOTADO, "
        "dilo y sugiere otro disponible. Si no sabes algo, dilo. "
        "No inventes productos ni precios. No puedes crear pedidos.\n\n"
        f"MENÚ:\n{construir_menu()}"
    )
    mensajes = [{"role": "system", "content": sistema}]
    if historial:
        mensajes.extend(historial)
    mensajes.append({"role": "user", "content": pregunta})

    payload = {
        "model": cfg["MODEL"],
        "stream": False,
        "messages": mensajes,
    }
    try:
        r = requests.post(cfg["URL"], json=payload, timeout=cfg["TIMEOUT"])
        r.raise_for_status()
        return r.json()["message"]["content"]
    except requests.exceptions.RequestException as e:
        raise ErrorIA(f"No se pudo contactar a Ollama: {e}")