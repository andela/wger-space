from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from wger.nutrition.models import NutritionPlan, Meal, MealItem
from wger.utils.cache import cache_mapper

signals = [post_save, post_delete]


@receiver(signals, sender=NutritionPlan)
@receiver(signals, sender=Meal)
@receiver(signals, sender=MealItem)
def cache_deletion_on_change(sender, instance, **kwargs):
    """
    delete cache key when there is a change
     in the nutrition plan, meals or mealitem
    """
    if sender == Meal:
        nutrition_plan_id = instance.plan_id
    elif sender == MealItem:
        nutrition_plan_id = Meal.objects.get(id=instance.meal_id).plan_id
    else:
        nutrition_plan_id = instance.id

    cache.delete(cache_mapper.get_nutrition_data(nutrition_plan_id))
