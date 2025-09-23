from django.conf import settings
from django.core.mail import send_mail
import africastalking


def send_order_email(order):
    """Send an email to admin about a new order."""

    subject = f"New order #{order.id} placed"

    message_lines = [
        f"Order ID: {order.id}",
        f"Customer: {order.customer.user.username}",
    ]

    for item in order.items.all():
        message_lines.append(
            f"- {item.quantity} x {item.product.name} @ {item.unit_price}"
        )

    message = "\n".join(message_lines)

    recipient = settings.ADMIN_EMAIL

    from_email = settings.DEFAULT_FROM_EMAIL

    send_mail(subject, message, from_email, [recipient], fail_silently=False)

    return True


def send_order_sms(order):
    """Send a confirmation SMS to the customer"""

    at_user = settings.AFRICASTALKING_USERNAME
    at_api_key = settings.AFRICASTALKING_KEY

    if not at_user or not at_api_key:
        return False

    to_number = order.customer.phone_number

    if not to_number:
        return False

    message = (
        f"Hi {order.customer.user.username}, your order #{order.id} has been received."
    )

    africastalking.initialize(username=at_user, api_key=at_api_key)
    sms = africastalking.SMS
    recipients = [to_number]
    sms.send(message, recipients)

    return True
