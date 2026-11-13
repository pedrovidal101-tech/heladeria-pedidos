from django.urls import path
from .views import AsistenteView, ConversacionesView, ConversacionDetalleView

urlpatterns = [
    path("asistente/", AsistenteView.as_view()),
    path("conversaciones/", ConversacionesView.as_view()),
    path("conversaciones/<int:pk>/", ConversacionDetalleView.as_view()),
]