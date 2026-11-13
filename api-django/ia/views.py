from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Conversacion, Mensaje
from .services import consultar_asistente, ErrorIA, interpretar_pedido

MAX_HISTORIAL = 10


class PreguntaSerializer(serializers.Serializer):
    pregunta = serializers.CharField(max_length=500)
    conversacion_id = serializers.IntegerField(required=False)


class AsistenteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PreguntaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        pregunta = serializer.validated_data["pregunta"]
        conv_id = serializer.validated_data.get("conversacion_id")

        conversacion = None
        historial = []
        if conv_id:
            try:
                conversacion = Conversacion.objects.get(
                    id=conv_id, usuario=request.user
                )
            except Conversacion.DoesNotExist:
                return Response(
                    {"error": "Conversación no encontrada."},
                    status=status.HTTP_404_NOT_FOUND,
                )
            previos = list(conversacion.mensajes.order_by("-id")[:MAX_HISTORIAL])
            previos.reverse()
            historial = [{"role": m.rol, "content": m.contenido} for m in previos]

        try:
            respuesta = consultar_asistente(pregunta, historial)
        except ErrorIA as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        if conversacion is None:
            conversacion = Conversacion.objects.create(
                usuario=request.user, titulo=pregunta[:100]
            )
        Mensaje.objects.create(conversacion=conversacion, rol="user", contenido=pregunta)
        Mensaje.objects.create(
            conversacion=conversacion, rol="assistant", contenido=respuesta
        )

        return Response({"conversacion_id": conversacion.id, "respuesta": respuesta})


class PedidoAsistenteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PreguntaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            items = interpretar_pedido(serializer.validated_data["pregunta"])
        except ErrorIA as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        return Response({"items": items})


class ConversacionesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        conversaciones = Conversacion.objects.filter(usuario=request.user).order_by(
            "-creada"
        )
        datos = [
            {"id": c.id, "titulo": c.titulo, "creada": c.creada}
            for c in conversaciones
        ]
        return Response(datos)


class ConversacionDetalleView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            conversacion = Conversacion.objects.get(id=pk, usuario=request.user)
        except Conversacion.DoesNotExist:
            return Response(
                {"error": "Conversación no encontrada."},
                status=status.HTTP_404_NOT_FOUND,
            )
        mensajes = [
            {"rol": m.rol, "contenido": m.contenido, "creado": m.creado}
            for m in conversacion.mensajes.all()
        ]
        return Response(
            {"id": conversacion.id, "titulo": conversacion.titulo, "mensajes": mensajes}
        )