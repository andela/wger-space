import datetime
import decimal
import logging

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from wger.core.tests.base_testcase import WorkoutManagerTestCase
from wger.utils.constants import TWOPLACES
from wger.weight.models import WeightEntry
from rest_framework.authtoken.models import Token

from io import StringIO
from django.core.management import call_command

import os
import logging
import tempfile
import shutil
from django.conf import settings

logger = logging.getLogger(__name__)


class UserCreationByApi(WorkoutManagerTestCase):

    def setUp(self):
        os.environ['RECAPTCHA_TESTING'] = 'True'
        if os.environ.get('TEST_MOBILE') == 'True':
            settings.FLAVOURS = ('mobile',)
            self.is_mobile = True

        # Set logging level
        logging.disable(logging.INFO)

        # Set MEDIA_ROOT
        self.media_root = tempfile.mkdtemp()
        settings.MEDIA_ROOT = self.media_root
        self.out = StringIO()
        User.objects.create(username='someone', password='password')
        profile = User.objects.get(username="someone")
        Token.objects.create(key='token', user=profile)
        self.command = call_command(
            'add-user-rest-api', 'token', 'someone', stdout=self.out)
        self.url = "/api/v2/user/creation/"

    def test_create_user_by_api(self):
        self.command
        response = self.client.post(
            self.url,
            data={
                "username": "new",
                "password": "password",
                "email": "new@new.com",
                "token": "token"})
        self.assertEqual(response.status_code, 201)

    def test_set_user_cant_be_set_twice(self):
        self.command
        self.client.post(
            self.url,
            data={
                "username": "new",
                "password": "password",
                "email": "new@new.com",
                "token": "token"})
        response = self.client.post(
            self.url,
            data={
                "username": "new",
                "password": "password",
                "email": "new@new.com",
                "token": "token"})
        self.assertEqual(response.status_code, 400)

    def test_set_user_cant_be_set_twice_with_same_email(self):
        self.command
        self.client.post(
            self.url,
            data={
                "username": "new",
                "password": "password",
                "email": "new@new.com",
                "token": "token"})
        response = self.client.post(
            self.url,
            data={
                "username": "new1",
                "password": "password",
                "email": "new@new.com",
                "token": "token"})
        self.assertEqual(response.status_code, 400)
        self.assertIn('user exists', response.data)

    def test_passord_should_be_8_to_11_characters(self):
        self.command
        response = self.client.post(
            self.url,
            data={
                "username": "new1",
                "password": "pass",
                "email": "new@new.com",
                "token": "token"})
        expected = {
            'password': ['Ensure this field has at least 8 characters.']}
        self.assertEqual(response.status_code, 400)
        self.assertEqual(expected, response.data)

    def test_cant_create_without_token(self):
        self.command
        response = self.client.post(
            self.url,
            data={
                "username": "new1",
                "password": "pass",
                "email": "new@new.com"})
        expected = {"detail": "Not found."}
        self.assertEqual(response.status_code, 404)
        self.assertEqual(expected, response.data)

    def test_cant_create_with_invalid_key(self):
        self.command
        response = self.client.post(
            self.url,
            data={
                "username": "new1",
                "password": "pass",
                "email": "new@new.com",
                "token": "toke"})
        expected = {"detail": "Not found."}
        self.assertEqual(response.status_code, 404)
        self.assertEqual(expected, response.data)
