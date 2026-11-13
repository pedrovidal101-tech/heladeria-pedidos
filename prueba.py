from modelos.pedido_dao import PedidoDAO

# 1. Crear un pedido para la Mesa 1 (id_mesa = 1)
id_creado = PedidoDAO.guardar_pedido(1, [])

# 2. Consultar pedidos que deben aparecer en la pantalla de la cocina
print("\n--- Pedidos para la Cocina ---")
pedidos = PedidoDAO.obtener_pedidos_pendientes()
for p in pedidos:
    print(f"Pedido #{p[0]} | Mesa {p[1]} | Estado: {p[2]} | Hora: {p[3]}")

# 3. Cambiar estado a 'en preparacion'
if id_creado:
    PedidoDAO.cambiar_estado(id_creado, "en preparacion")