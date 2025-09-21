from django.db import migrations


def create_order_statuses(apps, schema_editor):
    OrderStatus = apps.get_model("orders", "OrderStatus")
    statuses = [
        ("pending", "Pending"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
        ("canceled", "Canceled"),
    ]
    for name, _display in statuses:
        OrderStatus.objects.get_or_create(name=name)


def delete_order_statuses(apps, schema_editor):
    OrderStatus = apps.get_model("orders", "OrderStatus")
    names = ["pending", "shipped", "delivered", "canceled"]
    OrderStatus.objects.filter(name__in=names).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(create_order_statuses, reverse_code=delete_order_statuses),
    ]
