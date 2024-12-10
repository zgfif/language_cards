from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
import os


# before run this command, please, set SU_USERNAME, SU_EMAIL and SU_PASSWORD as env variables
class Command(BaseCommand):
    help = 'Create a superuser with predefined credentials'

    def handle(self, *args, **kwargs):
        SU_USERNAME = os.environ.get('SU_USERNAME', False)
        SU_EMAIL = os.environ.get('SU_EMAIL', False)
        SU_PASSWORD = os.environ.get('SU_PASSWORD', False)

        SU_CREDENTIALS = { 'SU_USERNAME': SU_USERNAME, 'SU_EMAIL': SU_EMAIL, 'SU_PASSWORD': SU_PASSWORD }

        if SU_USERNAME and SU_EMAIL and SU_PASSWORD:
            if User.objects.filter(username=SU_USERNAME).exists():
                self.print_warning('Superuser already exists')
            else:
                User.objects.create_superuser(username=SU_USERNAME, email=SU_EMAIL, password=SU_PASSWORD)
                self.print_success('Superuser has been successfully created!')

        else:
            self.stdout.write('Please, set env variable(s):')
            
            for key, value in SU_CREDENTIALS.items():
                if not value:
                    self.print_warning(key)

    def print_success(self, message=''):
        self.stdout.write(self.style.SUCCESS(message))

    def print_warning(self, message=''):
        self.stdout.write(self.style.WARNING(message))

