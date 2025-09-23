from types import SimpleNamespace
from unittest.mock import patch

from django.test import SimpleTestCase, override_settings

from orders.notifications import send_order_sms
from orders.notifications import send_order_email
from django.core import mail


class SendOrderSMSTest(SimpleTestCase):
    @override_settings(
        AFRICASTALKING_USERNAME="test_user", AFRICASTALKING_KEY="test_key"
    )
    @patch("orders.notifications.africastalking.SMS")
    @patch("orders.notifications.africastalking.initialize")
    def test_initialize_called_with_correct_credentials(self, mock_init, mock_sms_cls):
        # build a minimal order-like object
        user = SimpleNamespace(username="alice")
        customer = SimpleNamespace(user=user, phone_number="+123456789")
        order = SimpleNamespace(id=1, customer=customer)

        # SMS.send is an instance method; configure the mock
        mock_sms = mock_sms_cls
        mock_sms.send.return_value = {"status": "success"}

        result = send_order_sms(order)

        self.assertTrue(result)
        # ensure initialize called with username and api_key in correct order
        mock_init.assert_called_once_with(username="test_user", api_key="test_key")
        # ensure SMS.send called
        mock_sms.send.assert_called()

    def test_send_order_sms_no_credentials_returns_false(self):
        # clear settings via override not used here, ensure function returns False when no creds
        user = SimpleNamespace(username="bob")
        customer = SimpleNamespace(user=user, phone_number="+1111111")
        order = SimpleNamespace(id=2, customer=customer)

        with override_settings(AFRICASTALKING_USERNAME=None, AFRICASTALKING_KEY=None):
            result = send_order_sms(order)
            self.assertFalse(result)

    def test_send_order_sms_no_phone_returns_false(self):
        user = SimpleNamespace(username="carol")
        customer = SimpleNamespace(user=user, phone_number=None)
        order = SimpleNamespace(id=3, customer=customer)

        with override_settings(AFRICASTALKING_USERNAME="u", AFRICASTALKING_KEY="k"):
            result = send_order_sms(order)
            self.assertFalse(result)


class SendOrderEmailTests(SimpleTestCase):
    def test_send_order_email_sends_mail(self):
        # construct minimal objects; Order needs id, customer (with user.username), and items with product.name and unit_price
        user = SimpleNamespace(username="dave")
        customer = SimpleNamespace(user=user)

        product = SimpleNamespace(name="Widget")
        item = SimpleNamespace(quantity=2, product=product, unit_price="9.99")

        class Items:
            def __init__(self, items):
                self._items = items

            def all(self):
                return self._items

        order = SimpleNamespace(id=10, customer=customer, items=Items([item]))

        with override_settings(
            ADMIN_EMAIL="admin@example.com", DEFAULT_FROM_EMAIL="noreply@example.com"
        ):
            # Django's send_mail uses the test outbox when running tests
            result = send_order_email(order)
            self.assertTrue(result)
            self.assertEqual(len(mail.outbox), 1)
            sent = mail.outbox[0]
            self.assertIn("New order #10 placed", sent.subject)
            self.assertIn("Order ID: 10", sent.body)
