from rest_framework import serializers

from catalog.models import Category, Product


class CategorySerializer(serializers.ModelSerializer):
    parent = serializers.PrimaryKeyRelatedField(
        allow_null=True, queryset=Category.objects.all()
    )

    class Meta:
        model = Category
        fields = ["id", "name", "parent", "created_at"]
        read_only_fields = ["created_at"]


class ProductSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Category.objects.all()
    )

    class Meta:
        model = Product
        fields = ["id", "name", "category", "price", "available", "created_at"]
        read_only_fields = ["created_at"]
