from django.test import TestCase
from decimal import Decimal
from django.db import transaction
from .models import Category, Product


class CategoryTests(TestCase):
    def setUp(self):
        # Create a category hierarchy:
        # All Products
        #   - Bakery
        #     - Bread ($2.50)
        #     - Cookies ($1.50)
        #   - Produce
        #     - Fruits
        #       - Apples ($0.50)
        #       - Bananas ($0.30)
        #     - Vegetables
        #       - Carrots ($0.75)

        self.all_products = Category.objects.create(name="All Products")

        # Bakery branch
        self.bakery = Category.objects.create(name="Bakery", parent=self.all_products)
        self.bread = Product.objects.create(name="Bread", price=Decimal("2.50"))
        self.bread.category.add(self.bakery)
        self.cookies = Product.objects.create(name="Cookies", price=Decimal("1.50"))
        self.cookies.category.add(self.bakery)

        # Produce branch
        self.produce = Category.objects.create(name="Produce", parent=self.all_products)
        self.fruits = Category.objects.create(name="Fruits", parent=self.produce)
        self.vegetables = Category.objects.create(
            name="Vegetables", parent=self.produce
        )

        # Fruits
        self.apples = Product.objects.create(name="Apples", price=Decimal("0.50"))
        self.apples.category.add(self.fruits)
        self.bananas = Product.objects.create(name="Bananas", price=Decimal("0.30"))
        self.bananas.category.add(self.fruits)

        # Vegetables
        self.carrots = Product.objects.create(name="Carrots", price=Decimal("0.75"))
        self.carrots.category.add(self.vegetables)

    def test_category_hierarchy(self):
        """Test MPTT correctly handles the category hierarchy"""
        self.assertEqual(
            self.all_products.get_descendants().count(), 4
        )  # bakery, produce, fruits, vegetables
        self.assertEqual(self.bakery.get_children().count(), 0)  # leaf category
        self.assertEqual(self.produce.get_children().count(), 2)  # fruits, vegetables

        # Test ancestor traversal
        self.assertIn(self.all_products, self.fruits.get_ancestors())
        self.assertIn(self.produce, self.fruits.get_ancestors())

    def test_average_price_calculation(self):
        """Test average price calculations at different levels of the hierarchy"""
        self.assertEqual(self.bakery.get_average_price(), Decimal("2.00"))

        self.assertEqual(self.fruits.get_average_price(), Decimal("0.40"))

        self.assertAlmostEqual(
            self.produce.get_average_price(), Decimal("0.52"), places=2
        )

        self.assertAlmostEqual(
            self.all_products.get_average_price(), Decimal("1.11"), places=2
        )

    def test_empty_category_average_price(self):
        """Test that empty categories return None for average price"""
        empty_category = Category.objects.create(name="Empty")
        self.assertIsNone(empty_category.get_average_price())
