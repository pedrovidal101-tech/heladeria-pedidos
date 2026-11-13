from django.db import models
from django.utils import timezone


class Mesa(models.Model):
    ESTADOS = [("libre", "libre"), ("ocupada", "ocupada")]

    id_mesa = models.AutoField(primary_key=True)
    numero = models.IntegerField()
    estado = models.CharField(max_length=20, choices=ESTADOS, default="libre")

    class Meta:
        db_table = "Mesas"
        managed = False

    def __str__(self):
        return f"Mesa {self.numero}"


class Producto(models.Model):
    id_producto = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    categoria = models.CharField(max_length=50, default="General")
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    disponible = models.BooleanField(default=True)

    class Meta:
        db_table = "Productos"
        managed = False

    def __str__(self):
        return f"{self.nombre} - ${self.precio}"


class Pedido(models.Model):
    ESTADOS = [
        ("pendiente", "pendiente"),
        ("en preparacion", "en preparacion"),
        ("listo", "listo"),
        ("entregado", "entregado"),
        ("cancelado", "cancelado"),
    ]

    id_pedido = models.AutoField(primary_key=True)
    mesa = models.ForeignKey(
        Mesa, on_delete=models.PROTECT, db_column="id_mesa", related_name="pedidos"
    )
    fecha_hora = models.DateTimeField(default=timezone.now)
    estado = models.CharField(max_length=20, choices=ESTADOS, default="pendiente")

    class Meta:
        db_table = "Pedidos"
        managed = False

    def __str__(self):
        return f"Pedido #{self.id_pedido} ({self.estado})"


class DetallePedido(models.Model):
    id_detalle = models.AutoField(primary_key=True)
    pedido = models.ForeignKey(
        Pedido, on_delete=models.CASCADE, db_column="id_pedido", related_name="detalles"
    )
    producto = models.ForeignKey(
        Producto, on_delete=models.PROTECT, db_column="id_producto"
    )
    cantidad = models.IntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = "DetallePedido"
        managed = False

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"