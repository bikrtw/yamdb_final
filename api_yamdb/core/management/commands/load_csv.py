import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from reviews import models

FILES_PATH = ['static', 'data']


class Command(BaseCommand):
    help = 'Loads a CSV files from static/data into the database'

    def handle(self, *args, **options):
        files_models = {
            'users': models.User,
            'category': models.Category,
            'genre': models.Genre,
            'titles': models.Title,
            'genre_title': models.GenreTitle,
            'review': models.Review,
            'comments': models.Comment,
        }

        row_replacements = {
            'category': 'category_id',
            'author': 'author_id',
        }

        for file_name, model in files_models.items():
            initial_count = model.objects.count()
            path = os.path.join(
                settings.BASE_DIR, *FILES_PATH, f'{file_name}.csv')
            print(f'Loading {path} into {model.__name__}')
            with open(path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    for key, new_key in row_replacements.items():
                        if key in row:
                            row[new_key] = row[key]
                            del row[key]
                    try:
                        model.objects.get_or_create(**row)
                    except Exception as e:
                        print(e)
            final_count = model.objects.count()
            print(f'{model.__name__} loaded: {final_count - initial_count}')
