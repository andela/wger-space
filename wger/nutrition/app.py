from django.apps import AppConfig


class Nutritionconfig(AppConfig):
    name = 'wger.nutrition'

    def ready(self):
        import wger.nutrition.signals
        return wger.nutrition.signals
