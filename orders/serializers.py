from rest_framework import serializers
from orders.models import Customer, OrderItem, Order
from catalog.models import Product


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ["id", "user", "phone_number"]


class OrderItemSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
    )

    class Meta:
        model = OrderItem
        fields = ["id", "product", "quantity", "unit_price", "created_at"]
        read_only_fields = ["unit_price", "created_at"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    # set customer from request.user in the view by using HiddenField
    customer = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Order
        fields = ["id", "customer", "items", "status", "created_at"]
        read_only_fields = ["created_at"]

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("Order must contain at least one item.")
        for item in value:
            qty = item.get("quantity", 0)
            if qty <= 0:
                raise serializers.ValidationError(
                    "Item quantity must be a positive integer."
                )
        return value

    def create(self, validated_data):
        items_data = validated_data.pop("items", [])

        # resolve customer: CurrentUserDefault gives a User instance; map to Customer profile
        user = validated_data.pop("customer", None)
        customer = None
        if user is not None:
            # find or create the Customer profile
            customer, _ = Customer.objects.get_or_create(user=user)

        # create order
        order = Order.objects.create(customer=customer, **validated_data)

        # create order items with snapshot of unit_price
        for item in items_data:
            product = item["product"]
            quantity = item.get("quantity", 1)
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                unit_price=product.price,
            )

        return order
