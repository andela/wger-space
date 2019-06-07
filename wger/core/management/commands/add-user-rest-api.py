from django.core.management.base import (
    BaseCommand, CommandError)
from wger.core.models import (
    ApiUserModel, User, UserProfile)
from rest_framework.authtoken.models import Token
from django.shortcuts import get_object_or_404
from django.http import Http404


class Command(BaseCommand):

    help = 'Creates user using api key '

    def add_arguments(self, parser):
        parser.add_argument('api_key', type=str)
        parser.add_argument('creator_username', type=str)

    def handle(self, *args, **options):
        private_key_check = Token.objects.filter(key=options['api_key'])
        try:
            get_object_or_404(User, username=options['creator_username'])
            if len(private_key_check) == 0:
                self.stdout.write(
                    self.style.ERROR(
                        'input the required data in all the right fields'))
            else:
                try:
                    user = User.objects.filter(
                        username=options['creator_username'])
                    UserProfile.objects.filter(user=user).update(
                        is_allowed=True)
                    self.stdout.write(
                        self.style.SUCCESS(
                            'permission granted to create users'))
                except User.DoesNotExist:
                    self.stdout.CommandError(
                        self.style.ERROR(
                            'these fields are required'))
        except Http404:
            self.stdout.write(
                self.style.WARNING(
                    'unauthorised access please login to finish task'))
