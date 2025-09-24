# core/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny  # Import this


class HealthCheckView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        """
        A simple health check endpoint.
        """
        return Response({"status": "ok"}, status=status.HTTP_200_OK)
