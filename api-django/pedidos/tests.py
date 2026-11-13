from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from .models import DetallePedido, Mesa, Pedido, Producto

# Las tablas reales son managed=False. En las pruebas dejamos que
# Django las cree en la base temporal.
for _modelo in (Mesa, Producto, Pedido, DetallePedido):
    _modelo._meta.managed = True

URL = "/api/pedidos/"
User = get_user_model()


class PedidoAPITests(APITestCase):
    def setUp(self):
        self.mesero = User.objects.create_user(username="mesero", password="Clave12345")
        self.client.force_authenticate(user=self.mesero)
        self.mesa = Mesa.objects.create(numero=1, estado="libre")
        self.helado = Producto.objects.create(
            nombre="Helado de vainilla", precio=5000, disponible=True
        )
        self.agotado = Producto.objects.create(
            nombre="Brownie", precio=8000, disponible=False
        )

    def crear_pedido(self, producto=None, cantidad=1, mesa=None):
        return self.client.post(
            URL,
            {
                "mesa": (mesa or self.mesa).id_mesa,
                "productos": [
                    {"producto": (producto or self.helado).id_producto,
                     "cantidad": cantidad}
                ],
            },
            format="json",
        )

    def test_crear_pedido_correcto(self):
        resp = self.crear_pedido(cantidad=2)
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(Pedido.objects.count(), 1)
        self.assertEqual(DetallePedido.objects.count(), 1)
        self.mesa.refresh_from_db()
        self.assertEqual(self.mesa.estado, "ocupada")

    def test_no_pedir_producto_no_disponible(self):
        resp = self.crear_pedido(producto=self.agotado)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(Pedido.objects.count(), 0)

    def test_no_pedir_cantidad_cero(self):
        resp = self.crear_pedido(cantidad=0)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(Pedido.objects.count(), 0)

    def test_mesa_inexistente(self):
        resp = self.client.post(
            URL,
            {"mesa": 9999, "productos": [{"producto": 1, "cantidad": 1}]},
            format="json",
        )
        self.assertEqual(resp.status_code, 400)

    def test_estado_invalido(self):
        self.crear_pedido()
        pedido = Pedido.objects.first()
        resp = self.client.patch(
            f"{URL}{pedido.id_pedido}/", {"estado": "volando"}, format="json"
        )
        self.assertEqual(resp.status_code, 400)

    def test_no_modificar_pedido_cerrado(self):
        pedido = Pedido.objects.create(mesa=self.mesa, estado="entregado")
        resp = self.client.patch(
            f"{URL}{pedido.id_pedido}/", {"estado": "pendiente"}, format="json"
        )
        self.assertEqual(resp.status_code, 400)
        pedido.refresh_from_db()
        self.assertEqual(pedido.estado, "entregado")

    def test_cancelar_libera_la_mesa(self):
        self.crear_pedido()
        pedido = Pedido.objects.first()
        resp = self.client.delete(f"{URL}{pedido.id_pedido}/")
        self.assertEqual(resp.status_code, 204)
        pedido.refresh_from_db()
        self.mesa.refresh_from_db()
        self.assertEqual(pedido.estado, "cancelado")
        self.assertEqual(self.mesa.estado, "libre")

    def test_no_cancelar_dos_veces(self):
        self.crear_pedido()
        pedido = Pedido.objects.first()
        primera = self.client.delete(f"{URL}{pedido.id_pedido}/")
        segunda = self.client.delete(f"{URL}{pedido.id_pedido}/")
        self.assertEqual(primera.status_code, 204)
        self.assertEqual(segunda.status_code, 400)


class SeguridadJWTTests(APITestCase):
    def setUp(self):
        self.mesero = User.objects.create_user(username="mesero", password="Clave12345")
        self.admin = User.objects.create_user(
            username="admin", password="Clave12345", is_staff=True
        )

    def test_sin_token_responde_401(self):
        resp = self.client.get("/api/productos/")
        self.assertEqual(resp.status_code, 401)

    def test_login_devuelve_token(self):
        resp = self.client.post(
            "/api/auth/token/",
            {"username": "mesero", "password": "Clave12345"},
            format="json",
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIn("access", resp.data)

    def test_mesero_no_puede_crear_producto(self):
        self.client.force_authenticate(user=self.mesero)
        resp = self.client.post(
            "/api/productos/",
            {"nombre": "Cono", "precio": "3000", "disponible": True},
            format="json",
        )
        self.assertEqual(resp.status_code, 403)

    def test_admin_si_puede_crear_producto(self):
        self.client.force_authenticate(user=self.admin)
        resp = self.client.post(
            "/api/productos/",
            {"nombre": "Cono", "precio": "3000", "disponible": True},
            format="json",
        )
        self.assertEqual(resp.status_code, 201)