from rest_framework import serializers

from .models import DetallePedido, Mesa, Pedido, Producto


class MesaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mesa
        fields = ["id_mesa", "numero", "estado"]


class ProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = ["id_producto", "nombre", "categoria", "precio", "disponible"]


class DetallePedidoSerializer(serializers.ModelSerializer):
    nombre_producto = serializers.CharField(source="producto.nombre", read_only=True)

    class Meta:
        model = DetallePedido
        fields = [
            "id_detalle",
            "producto",
            "nombre_producto",
            "cantidad",
            "precio_unitario",
        ]
        read_only_fields = ["precio_unitario"]


class PedidoSerializer(serializers.ModelSerializer):
    detalles = DetallePedidoSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()

    class Meta:
        model = Pedido
        fields = ["id_pedido", "mesa", "fecha_hora", "estado", "detalles", "total"]
        read_only_fields = ["fecha_hora"]

    def get_total(self, pedido):
        return sum(d.cantidad * d.precio_unitario for d in pedido.detalles.all())