from django.conf import settings
from django.db import models


class Conversacion(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="conversaciones",
    )
    titulo = models.CharField(max_length=100, blank=True)
    creada = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Conversación {self.id} de {self.usuario}"


class Mensaje(models.Model):
    ROLES = [
        ("user", "Usuario"),
        ("assistant", "Asistente"),
    ]

    conversacion = models.ForeignKey(
        Conversacion,
        on_delete=models.CASCADE,
        related_name="mensajes",
    )
    rol = models.CharField(max_length=10, choices=ROLES)
    contenido = models.TextField()
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["creado"]

    def __str__(self):
        return f"{self.rol}: {self.contenido[:40]}"