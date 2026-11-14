from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .semantica import buscar_productos


class BusquedaSemanticaView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        q = request.query_params.get("q", "").strip()
        if not q:
            return Response(
                {"error": "Debes escribir qué buscas (parámetro q)."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            cantidad = int(request.query_params.get("cantidad", 3))
            if cantidad < 1 or cantidad > 10:
                raise ValueError
        except ValueError:
            return Response(
                {"error": "La cantidad debe estar entre 1 y 10."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            productos = buscar_productos(q, cantidad)
        except Exception as e:
            return Response(
                {
                    "error": "No fue posible realizar la búsqueda semántica.",
                    "detalle": str(e),
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        return Response(
            {
                "pregunta": q,
                "total_resultados": len(productos),
                "resultados": [
                    {
                        "id_producto": p.id_producto,
                        "nombre": p.nombre,
                        "categoria": p.categoria,
                        "precio": str(p.precio),
                    }
                    for p in productos
                ],
            }
        )