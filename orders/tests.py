from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIRequestFactory
from decimal import Decimal

from catalog.models import Category, Product
from .models import Customer, Order, OrderItem, OrderStatus
from .serializers import OrderSerializer


class OrderSerializerTests(TestCase):
    def setUp(self):
        # Create a test user and customer
        self.user = User.objects.create_user(
            username="testuser", password="testpass123", email="test@example.com"
        )
        self.customer = Customer.objects.create(
            user=self.user, phone_number="+1234567890"
        )

        # Create some test products
        self.category = Category.objects.create(name="Test Category")
        self.product1 = Product.objects.create(
            name="Test Product 1", price=Decimal("10.00")
        )
        self.product1.category.add(self.category)

        self.product2 = Product.objects.create(
            name="Test Product 2", price=Decimal("20.00")
        )
        self.product2.category.add(self.category)

        # Create pending status
        self.pending_status = OrderStatus.objects.create(name="pending")

    def test_order_creation_with_authenticated_user(self):
        """Test creating an order through the serializer with an authenticated user"""
        factory = APIRequestFactory()
        request = factory.post("/api/orders/")
        request.user = self.user

        # Prepare order data
        order_data = {
            "items": [
                {"product": self.product1.id, "quantity": 2},
                {"product": self.product2.id, "quantity": 1},
            ],
            "status": self.pending_status.id,
        }

        # Create serializer with request context
        serializer = OrderSerializer(data=order_data, context={"request": request})

        # Validate and save
        self.assertTrue(serializer.is_valid(), serializer.errors)
        order = serializer.save()

        # Verify order was created correctly
        self.assertEqual(order.customer.user, self.user)
        self.assertEqual(order.items.count(), 2)

        # Verify items and prices
        items = order.items.all()
        self.assertEqual(items[0].quantity, 2)
        self.assertEqual(items[0].unit_price, Decimal("10.00"))
        self.assertEqual(items[1].quantity, 1)
        self.assertEqual(items[1].unit_price, Decimal("20.00"))

    def test_order_creation_validation(self):
        """Test order validation rules"""
        factory = APIRequestFactory()
        request = factory.post("/api/orders/")
        request.user = self.user

        # Test empty items list
        order_data = {"items": [], "status": self.pending_status.id}
        serializer = OrderSerializer(data=order_data, context={"request": request})
        self.assertFalse(serializer.is_valid())
        self.assertIn("items", serializer.errors)

        # Test invalid quantity
        order_data = {
            "items": [{"product": self.product1.id, "quantity": 0}],
            "status": self.pending_status.id,
        }
        serializer = OrderSerializer(data=order_data, context={"request": request})
        self.assertFalse(serializer.is_valid())
        self.assertIn("items", serializer.errors)
