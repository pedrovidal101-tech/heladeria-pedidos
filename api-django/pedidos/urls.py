from rest_framework.routers import DefaultRouter

from .views import MesaViewSet, PedidoViewSet, ProductoViewSet

router = DefaultRouter()
router.register("mesas", MesaViewSet)
router.register("productos", ProductoViewSet)
router.register("pedidos", PedidoViewSet)

urlpatterns = router.urls