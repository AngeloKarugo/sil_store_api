from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from catalog.models import Category, Product
from .serializers import CategorySerializer, ProductSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    @action(detail=True, methods=["get"])
    def average_price(self, request, pk=None):
        category = self.get_object()
        avg = category.get_average_price()
        return Response({"average_price": avg})


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
