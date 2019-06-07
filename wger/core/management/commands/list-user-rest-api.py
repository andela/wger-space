from django.core.management.base import (
    BaseCommand, CommandError)
from wger.core.models import (
    ApiUserModel, User)
from django_tabulate import tabulate_qs
from tabulate import tabulate


class Command(BaseCommand):

    help = 'retrieves all users created via the API'

    def add_arguments(self, parser):
        parser.add_argument('creator_username', type=str)

    def handle(self, *args, **options):
        try:
            user = User.objects.filter(username=options['creator_username'])
            list_of_users_created = ApiUserModel.objects.filter(
                creator=user).select_related('user_being_created')
            list_user = []
            for user in list_of_users_created:
                list_user.append(
                    [
                        user.user_being_created.username, user.creator.username
                    ]
                )
                self.stdout.write(self.style.MIGRATE_HEADING(
                    tabulate(list_user, headers=["USER", "CREATOR"],
                             tablefmt="github")))
        except CommandError:
            self.stdout.write(
                self.style.ERROR('user not found'))
