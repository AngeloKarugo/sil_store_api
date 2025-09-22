from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIRequestFactory
from decimal import Decimal

from catalog.models import Category, Product
from .models import Customer, Order, OrderItem, OrderStatus
from .serializers import OrderSerializer

from rest_framework.test import APIClient


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
        # Get pending status
        self.pending_status, _ = OrderStatus.objects.get_or_create(name="pending")

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

    def test_order_creation_via_api_and_category_avg(self):
        """Integration test: create products/categories and place order via API, then query category average"""
        client = APIClient()
        client.login(username="testuser", password="testpass123")

        # call category average endpoint
        cat_url = f"/api/categories/{self.category.id}/average_price/"
        resp = client.get(cat_url)
        self.assertEqual(resp.status_code, 200)
        self.assertIn("average_price", resp.json())

        # place order via API
        order_url = "/api/orders/"
        order_data = {
            "items": [
                {"product": self.product1.id, "quantity": 1},
                {"product": self.product2.id, "quantity": 2},
            ],
            "status": self.pending_status.id,
        }
        from unittest.mock import patch

        with patch("orders.notifications.send_order_email") as mock_email, patch(
            "orders.notifications.send_order_sms"
        ) as mock_sms:
            resp = client.post(order_url, order_data, format="json")
            self.assertIn(resp.status_code, (200, 201))
            body = resp.json()
            self.assertIn("id", body)
            mock_email.assert_called()
            mock_sms.assert_called()
