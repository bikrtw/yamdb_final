from django.core.management.base import BaseCommand
from reviews import models


class Command(BaseCommand):

    def handle(self, *args, **options):
        objects_to_delete = [
            models.Comment,
            models.Review,
            models.GenreTitle,
            models.Title,
            models.Genre,
            models.Category,
            models.User,
        ]

        print('Clearing database...')

        for model in objects_to_delete:
            initial_count = model.objects.count()
            model.objects.all().delete()
            new_count = model.objects.count()
            print(f'{model.__name__}: {initial_count} -> {new_count}')

        print('Done.')
