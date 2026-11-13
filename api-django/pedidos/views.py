from django.db import transaction
from django.db.models import ProtectedError
from rest_framework import serializers, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import DetallePedido, Mesa, Pedido, Producto
from .permissions import LecturaAutenticadaEscrituraAdmin
from .serializers import MesaSerializer, PedidoSerializer, ProductoSerializer

ESTADOS_ACTIVOS = ("pendiente", "en preparacion", "listo")
ESTADOS_CERRADOS = ("entregado", "cancelado")


def liberar_mesa_si_corresponde(mesa):
    """Deja la mesa libre si ya no tiene pedidos activos."""
    if not Pedido.objects.filter(mesa=mesa, estado__in=ESTADOS_ACTIVOS).exists():
        mesa.estado = "libre"
        mesa.save(update_fields=["estado"])


class ProtegidoMixin:
    """Si algo no se puede eliminar porque tiene pedidos asociados, responde 409."""

    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except ProtectedError:
            return Response(
                {"detalle": "No se puede eliminar: tiene pedidos asociados."},
                status=status.HTTP_409_CONFLICT,
            )


class MesaViewSet(ProtegidoMixin, viewsets.ModelViewSet):
    queryset = Mesa.objects.all().order_by("numero")
    serializer_class = MesaSerializer
    permission_classes = [LecturaAutenticadaEscrituraAdmin]


class ProductoViewSet(ProtegidoMixin, viewsets.ModelViewSet):
    queryset = Producto.objects.all().order_by("nombre")
    serializer_class = ProductoSerializer
    permission_classes = [LecturaAutenticadaEscrituraAdmin]


class PedidoViewSet(viewsets.ModelViewSet):
    queryset = (
        Pedido.objects.select_related("mesa")
        .prefetch_related("detalles__producto")
        .order_by("id_pedido")
    )
    serializer_class = PedidoSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        """POST: {"mesa": 2, "productos": [{"producto": 3, "cantidad": 2}]}"""
        try:
            mesa = Mesa.objects.get(pk=request.data.get("mesa"))
        except (Mesa.DoesNotExist, ValueError, TypeError):
            return Response(
                {"mesa": "La mesa no existe."}, status=status.HTTP_400_BAD_REQUEST
            )

        items = request.data.get("productos")
        if not isinstance(items, list) or not items:
            return Response(
                {"productos": "Envía al menos un producto."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            pedido = Pedido.objects.create(mesa=mesa, estado="pendiente")
            for item in items:
                try:
                    cantidad = int(item.get("cantidad", 1))
                    producto = Producto.objects.filter(
                        pk=item.get("producto"), disponible=True
                    ).first()
                except (ValueError, TypeError, AttributeError):
                    raise serializers.ValidationError(
                        {"productos": "Formato de producto inválido."}
                    )
                if producto is None or cantidad < 1:
                    raise serializers.ValidationError(
                        {"productos": "Producto no disponible o cantidad inválida."}
                    )
                DetallePedido.objects.create(
                    pedido=pedido,
                    producto=producto,
                    cantidad=cantidad,
                    precio_unitario=producto.precio,
                )
            mesa.estado = "ocupada"
            mesa.save(update_fields=["estado"])

        return Response(
            self.get_serializer(pedido).data, status=status.HTTP_201_CREATED
        )

    def update(self, request, *args, **kwargs):
        """PUT/PATCH: {"estado": "listo"}. Solo cambia el estado del pedido."""
        pedido = self.get_object()
        if pedido.estado in ESTADOS_CERRADOS:
            return Response(
                {"estado": "El pedido ya está cerrado y no se puede modificar."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        nuevo_estado = request.data.get("estado")
        if nuevo_estado not in [e[0] for e in Pedido.ESTADOS]:
            return Response(
                {"estado": "Estado inválido."}, status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            pedido.estado = nuevo_estado
            pedido.save(update_fields=["estado"])
            if nuevo_estado in ESTADOS_ACTIVOS:
                pedido.mesa.estado = "ocupada"
                pedido.mesa.save(update_fields=["estado"])
            else:
                liberar_mesa_si_corresponde(pedido.mesa)

        return Response(self.get_serializer(pedido).data)

    def destroy(self, request, *args, **kwargs):
        """DELETE: cancela el pedido (queda en la BD) y libera la mesa."""
        pedido = self.get_object()
        if pedido.estado in ESTADOS_CERRADOS:
            return Response(
                {"estado": "El pedido ya está cerrado y no se puede cancelar."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            pedido.estado = "cancelado"
            pedido.save(update_fields=["estado"])
            liberar_mesa_si_corresponde(pedido.mesa)
        return Response(status=status.HTTP_204_NO_CONTENT)