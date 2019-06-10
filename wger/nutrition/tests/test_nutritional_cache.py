from wger.nutrition.models import NutritionPlan, Meal, MealItem
from wger.core.tests.base_testcase import WorkoutManagerTestCase
from wger.utils.cache import cache_mapper
from wger.core.models import Language
from django.core.cache import cache
from django.contrib.auth.models import User


class NutritionPlanCacheTestCase(WorkoutManagerTestCase):

    def create_nutrition_plan(self):
        nutrition_plan = NutritionPlan()
        nutrition_plan.user = User.objects.create_user(username='sebbss')
        nutrition_plan.language = Language.objects.get(short_name='en')
        nutrition_plan.save()

        meal = Meal()
        meal.plan = nutrition_plan
        meal.order = 1
        meal.save()

        meal_item = MealItem()
        meal_item.meal = meal
        meal_item.amount = 1
        meal_item.ingredient_id = 1
        meal_item.order = 1
        return [nutrition_plan, meal, meal_item]

    def test_cache_creation(self):
        nutrition_plan = self.create_nutrition_plan()[0]
        nutrition_plan.get_nutritional_values()
        self.assertTrue(
            cache.get(cache_mapper.get_nutrition_data(nutrition_plan)))

    def test_change_in_meal(self):
        nutrition_object = self.create_nutrition_plan()
        nutrition_plan = nutrition_object[0]
        nutrition_plan.get_nutritional_values()
        meal = nutrition_object[1]
        self.assertTrue(
            cache.get(cache_mapper.get_nutrition_data(nutrition_plan)))
        meal.save()
        self.assertFalse(
            cache.get(cache_mapper.get_nutrition_data(nutrition_plan)))
        nutrition_plan.get_nutritional_values()
        self.assertTrue(
            cache.get(cache_mapper.get_nutrition_data(nutrition_plan)))
        meal.delete()
        self.assertFalse(
            cache.get(cache_mapper.get_nutrition_data(nutrition_plan)))

    def test_change_in_meal_item(self):
        nutrition_object = self.create_nutrition_plan()
        nutrition_plan = nutrition_object[0]
        nutrition_plan.get_nutritional_values()
        meal_item = nutrition_object[2]
        self.assertTrue(
            cache.get(cache_mapper.get_nutrition_data(nutrition_plan)))
        meal_item.save()
        self.assertFalse(
            cache.get(cache_mapper.get_nutrition_data(nutrition_plan)))
        nutrition_plan.get_nutritional_values()
        self.assertTrue(
            cache.get(cache_mapper.get_nutrition_data(nutrition_plan)))
        meal_item.delete()
        self.assertFalse(
            cache.get(cache_mapper.get_nutrition_data(nutrition_plan)))

    def test_change_in_nutrition_plan(self):
        nutrition_plan = self.create_nutrition_plan()[0]
        nutrition_plan.get_nutritional_values()
        self.assertTrue(
            cache.get(cache_mapper.get_nutrition_data(nutrition_plan)))
        nutrition_plan.save()
        self.assertFalse(
            cache.get(cache_mapper.get_nutrition_data(nutrition_plan)))
        nutrition_plan.get_nutritional_values()
        self.assertTrue(
            cache.get(cache_mapper.get_nutrition_data(nutrition_plan)))
        nutrition_plan.delete()
        self.assertFalse(
            cache.get(cache_mapper.get_nutrition_data(nutrition_plan)))
