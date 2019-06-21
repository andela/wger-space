# -*- coding: utf-8 -*-

# This file is part of wger Workout Manager.
#
# wger Workout Manager is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# wger Workout Manager is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
import logging
import json
import requests
import os

from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext_lazy

from django.views.generic import CreateView, UpdateView

from wger.nutrition.models import NutritionPlan, Meal, MealItem
from wger.utils.generic_views import WgerFormMixin
from wger.nutrition.forms import MealItemForm


logger = logging.getLogger(__name__)


# ************************
# Meal functions
# ************************


class MealCreateView(WgerFormMixin, CreateView):
    """
    Generic view to add a new meal to a nutrition plan
    """

    model = MealItem
    title = ugettext_lazy("Add new meal")
    owner_object = {"pk": "plan_pk", "class": NutritionPlan}
    form_class = MealItemForm
    template_name = "meal_item/add.html"

    def form_valid(self, form):
        time = self.request.POST["time-field"]
        if time == '':
            time = None
        amount = self.request.POST['amount']
        ingredient = self.request.POST['ingredient']
        weight_unit = self.request.POST['weight_unit']
        plan_id = self.kwargs['plan_pk']

        url = os.environ.get("MEAL_MEALITEM_URL")
        payload = {
            "time": time,
            "amount": amount,
            "ingredient": ingredient,
            "weight_unit": weight_unit,
            "plan_id": plan_id
        }
        headers = {"content-type": "application/json"}
        requests.post(
            url,
            data=json.dumps(payload),
            headers=headers
        )

        return HttpResponseRedirect(
            reverse("nutrition:plan:view",
                    kwargs={"id": plan_id})
        )

    def get_success_url(self):
        return self.object.plan.get_absolute_url()

    # Send some additional data to the template
    def get_context_data(self, **kwargs):
        context = super(MealCreateView, self).get_context_data(**kwargs)
        context["form_action"] = reverse(
            "nutrition:meal:add", kwargs={"plan_pk": self.kwargs["plan_pk"]}
        )
        context["plan_id"] = self.kwargs["plan_pk"]
        context["ingredient_searchfield"] = self.request.POST.get(
            "ingredient_searchfield", ""
        )

        return context


class MealEditView(WgerFormMixin, UpdateView):
    """
    Generic view to update an existing meal
    """

    model = Meal
    fields = "__all__"
    title = ugettext_lazy("Edit meal")
    form_action_urlname = "nutrition:meal:edit"

    def get_success_url(self):
        return self.object.plan.get_absolute_url()


@login_required
def delete_meal(request, id):
    """
    Deletes the meal with the given ID
    """

    # Load the meal
    meal = get_object_or_404(Meal, pk=id)
    plan = meal.plan

    # Only delete if the user is the owner
    if plan.user == request.user:
        meal.delete()
        return HttpResponseRedirect(plan.get_absolute_url())
    else:
        return HttpResponseForbidden()
