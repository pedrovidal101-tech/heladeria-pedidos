import json

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


def construir_contexto_semantico(pregunta):
    """Productos relacionados por significado (ChromaDB).
    Si falla, el asistente sigue funcionando solo con el menú."""
    try:
        from ia.semantica import buscar_productos

        productos = buscar_productos(pregunta, cantidad=3)
    except Exception:
        return "No disponible."
    if not productos:
        return "Sin coincidencias."
    return "\n".join(f"- {p.nombre} ({p.categoria})" for p in productos)


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
        "No inventes productos ni precios. Los pedidos los crea el mesero desde su "
        "pantalla, tú no los guardas. Sé conversador y cálido: saluda, haz una "
        "pregunta corta para conocer el gusto del cliente y recomienda combos con "
        "productos reales del menú, por ejemplo un helado con brownie, indicando "
        "siempre el nombre y el precio de cada producto y el total de la suma, con "
        "este formato: Te recomiendo un Helado de Vainilla ($4.500) y un Brownie con "
        "Helado ($12.000), total $16.500. Si preguntan algo que no tiene que ver con "
        "la heladería, responde amable en una frase y vuelve al menú. Los productos "
        "relacionados son sugerencias por significado: confirma que estén en el menú "
        "y no los uses para saber la disponibilidad.\n\n"
        f"MENÚ:\n{construir_menu()}\n\n"
        f"PRODUCTOS RELACIONADOS CON LA PREGUNTA:\n{construir_contexto_semantico(pregunta)}"
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


def interpretar_pedido(texto):
    """Convierte lo que dicta el mesero en una lista de productos validada."""
    cfg = settings.OLLAMA_CONFIG
    productos = list(Producto.objects.filter(disponible=True))
    menu = "\n".join(f"{p.id_producto}: {p.nombre}" for p in productos)
    sistema = (
        "Conviertes pedidos de una heladería en JSON. "
        "Usa SOLO los productos de esta lista (id: nombre):\n"
        f"{menu}\n\n"
        'Responde SOLO con JSON así: {"items": [{"producto": 1, "cantidad": 2}]}. '
        'Si el texto no pide ningún producto de la lista, responde {"items": []}.'
    )
    payload = {
        "model": cfg["MODEL"],
        "stream": False,
        "format": "json",
        "messages": [
            {"role": "system", "content": sistema},
            {"role": "user", "content": texto},
        ],
    }
    try:
        r = requests.post(cfg["URL"], json=payload, timeout=cfg["TIMEOUT"])
        r.raise_for_status()
        datos = json.loads(r.json()["message"]["content"])
    except requests.exceptions.RequestException as e:
        raise ErrorIA(f"No se pudo contactar a Ollama: {e}")
    except (ValueError, KeyError):
        raise ErrorIA("La IA no devolvió un pedido válido.")

    por_id = {p.id_producto: p for p in productos}
    crudos = datos.get("items", []) if isinstance(datos, dict) else []
    items = []
    for it in crudos if isinstance(crudos, list) else []:
        try:
            pid = int(it.get("producto"))
            cantidad = int(it.get("cantidad", 1))
        except (ValueError, TypeError, AttributeError):
            continue
        if pid in por_id and 1 <= cantidad <= 20:
            items.append(
                {"producto": pid, "nombre": por_id[pid].nombre, "cantidad": cantidad}
            )
    return items