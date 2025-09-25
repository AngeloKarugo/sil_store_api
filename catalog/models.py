from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from django.forms import ValidationError
from django.db.models import Avg


class Category(MPTTModel):
    name = models.CharField(max_length=100, unique=True)
    parent = TreeForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="subcategories",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def get_average_price(self):
        """
        Return the average price of all products assigned to this category
        or any of its descendant categories.
        """
        # collect products for this category and all descendants
        descendant_categories = self.get_descendants(include_self=True)
        # product queryset through M2M 'products' related_name
        from django.db.models import F

        qs = Product.objects.filter(category__in=descendant_categories)
        return qs.aggregate(avg_price=Avg("price"))["avg_price"]


class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ManyToManyField(Category, related_name="products")
    available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
