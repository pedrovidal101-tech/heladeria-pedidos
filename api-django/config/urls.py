from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/", include("pedidos.urls")),
    
    path('api/ia/', include('ia.urls')),
    path('chat/', TemplateView.as_view(template_name='ia/chat.html')),
    
    path('mesero/', TemplateView.as_view(template_name='ia/mesero.html')),
    path('cocina/', TemplateView.as_view(template_name='ia/cocina.html')),
]