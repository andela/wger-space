from io import StringIO
from django.core.management import call_command
from django.test import TestCase
from ..tests.base_testcase import WorkoutManagerTestCase as login_method
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from django.conf import settings
import os
import logging
import tempfile
import shutil
from django.core.management.base import CommandError
from wger.core.models import ApiUserModel
from django.core.urlresolvers import reverse


class CreateUserCommand(login_method):

    def setUp(self):
        self.client = APIClient()
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
        User.objects.create(username='good', password='good')

    def test_user_permissions(self):
        self.user_login('good')
        user = User.objects.get(username='good')
        # create a new key
        Token.objects.create(key='group', user=user)
        call_command(
            'add-user-rest-api', 'group', 'good', stdout=self.out)
        self.assertIn(
            'permission granted to create users',
            self.out.getvalue())

    def test_get_list_of_users(self):
        self.user_login('good')
        call_command(
            'list-user-rest-api', 'test', stdout=self.out)
        self.assertIsNotNone
