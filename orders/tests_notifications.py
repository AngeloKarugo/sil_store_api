from types import SimpleNamespace
from unittest.mock import patch

from django.test import SimpleTestCase, override_settings

from orders.notifications import send_order_sms


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
