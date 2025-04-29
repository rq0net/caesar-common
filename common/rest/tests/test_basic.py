import unittest

from rest_framework import status
from rest_framework.reverse import reverse
from django.conf import settings

from caesar_auth.rest.tests.base import BaseTestCase


class BasicTestCase(BaseTestCase):

    def test_authorization_is_enforced(self):
        """Test that the api has user authorization."""
        response = self.client.get(reverse('icinga'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_access_with_false_credential(self):
        response = self.basics_auth_get(
            reverse('icinga'),
            username=settings.TEST_ADMIN_USER,
            password=settings.TEST_ADMIN_PASS
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_access_with_false_token(self):
        false_token = "c2dffbda4f73937afb13ce8dc281759a8b"
        response = self.token_auth_get(
            reverse('icinga'),
            false_token
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


if __name__ == '__main__':
    unittest.main()
