from django.urls import path
from .views import (
    AsistenteView,
    ConversacionesView,
    ConversacionDetalleView,
    PedidoAsistenteView,
)
from .views_semantica import BusquedaSemanticaView

urlpatterns = [
    path("asistente/", AsistenteView.as_view()),
    path("asistente/pedido/", PedidoAsistenteView.as_view()),
    path("buscar/", BusquedaSemanticaView.as_view()),
    path("conversaciones/", ConversacionesView.as_view()),
    path("conversaciones/<int:pk>/", ConversacionDetalleView.as_view()),
]