import json

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


PATH: str = './ingredients.json'


class Command(BaseCommand):
    def handle(self, *args, **options):
        data_for_download: list = []

        with open(PATH, 'rb') as file:
            objects_data = json.load(file)

            for object_data in objects_data:
                data_for_download.append(Ingredient(**object_data))
            Ingredient.objects.bulk_create(data_for_download)
        print('finished')
