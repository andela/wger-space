# This file is part of Workout Manager.
# 
# Workout Manager is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Workout Manager is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU Affero General Public License
import logging
import json

from django.template import RequestContext
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import HttpResponseForbidden
from django.core.context_processors import csrf
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.forms import ModelForm
from django.utils.translation import ugettext as _

from nutrition.models import NutritionPlan
from nutrition.models import Meal
from nutrition.models import MealItem
from nutrition.models import Ingredient

from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4, cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Table
from reportlab.lib import colors

from exercises.views import load_language

logger = logging.getLogger('workout_manager.custom')


# ************************
# Plan functions
# ************************

class PlanForm(ModelForm):
    class Meta:
        model = NutritionPlan
        exclude=('user', 'language', )

@login_required
def overview(request):
    template_data = {}
    template_data.update(csrf(request))
    template_data['active_tab'] = 'nutrition'
    
    plans  = NutritionPlan.objects.filter(user = request.user)
    template_data['plans'] = plans
    
    return render_to_response('nutrition_overview.html',
                              template_data,
                              context_instance=RequestContext(request))

@login_required
def add(request):
    """Add a new nutrition plan and redirect to its page
    """
    
    plan = NutritionPlan()
    plan.user = request.user
    plan.language = load_language()
    plan.save()
    
    return HttpResponseRedirect('/nutrition/%s/view/' % plan.id)


@login_required
def view(request, id):
    """Show the nutrition plan with the given ID
    """
    template_data = {}
    template_data['active_tab'] = 'nutrition'
    
    plan = get_object_or_404(NutritionPlan, pk=id, user=request.user)
    template_data['plan'] = plan
    
    # Sum the nutrional info
    nutritional_info = {'energy': 0,
                        'protein': 0,
                        'carbohydrates': 0,
                        'fat': 0,
                        'fibres': 0,
                        'natrium': 0}
    for meal in plan.meal_set.select_related():
        for item in meal.mealitem_set.select_related():
            
            # Don't proceed if the ingredient was input by hand or has freetext units
            if item.ingredient and item.amount_gramm:
                nutritional_info['energy'] += item.ingredient.energy * item.amount_gramm / 100
                nutritional_info['protein'] += item.ingredient.protein  * item.amount_gramm / 100
                nutritional_info['carbohydrates'] += item.ingredient.carbohydrates  * item.amount_gramm / 100
                nutritional_info['fat'] += item.ingredient.fat  * item.amount_gramm / 100
                
                if item.ingredient.fibres:
                    nutritional_info['fibres'] += item.ingredient.fibres  * item.amount_gramm / 100
                
                if item.ingredient.natrium:
                    nutritional_info['natrium'] += item.ingredient.natrium  * item.amount_gramm / 100
    template_data['nutritional_data'] = nutritional_info
    
    
    return render_to_response('view_nutrition_plan.html', 
                              template_data,
                              context_instance=RequestContext(request))

@login_required
def edit_plan(request, id):
    """Edits a nutrition plan
    """
    template_data = {}
    template_data['active_tab'] = 'nutrition'
    
    # Load the plan
    plan = get_object_or_404(NutritionPlan, pk=id, user=request.user)
    template_data['plan'] = plan
    
    # Process request
    if request.method == 'POST':
        form = PlanForm(request.POST, instance=plan)
        
        # If the data is valid, save and redirect
        if form.is_valid():
            plan = form.save(commit=False)
            #plan.language = load_language()
            plan.save()
            
            return HttpResponseRedirect('/nutrition/%s/view/' % id)
    else:
        form = PlanForm(instance=plan)
    template_data['form'] = form
    
    
    return render_to_response('edit_plan.html', 
                              template_data,
                              context_instance=RequestContext(request))

def export_pdf(request, id):
    """Generates a PDF with the contents of a nutrition plan
    
    See also
    * http://www.blog.pythonlibrary.org/2010/09/21/reportlab-tables-creating-tables-in-pdfs-with-python/
    * http://www.reportlab.com/apis/reportlab/dev/platypus.html
    """
    
    #Load the workout
    plan = get_object_or_404(NutritionPlan, pk=id, user=request.user)
    
    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(mimetype='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=plan.pdf'
    
    # Create the PDF object, using the response object as its "file."
    doc = SimpleDocTemplate(response,
                            pagesize = A4,
                            title = _('Workout'),
                            author = _('Workout Manager'),
                            subject = _('Nutritional plan %s') % request.user.username)

    # container for the 'Flowable' objects
    elements = []
    
    styleSheet = getSampleStyleSheet()
    data = []
    
    # Iterate through the Plan
    meal_markers = []
    ingredient_markers = []
    
    
    # Meals
    for meal in plan.meal_set.select_related():
        meal_markers.append(len(data))
    
        P = Paragraph('<para align="center"><strong>%s</strong></para>' % meal.time,
                      styleSheet["Normal"])
    
        data.append([P])
        
        # Ingredients
        for item in meal.mealitem_set.select_related():
            ingredient_markers.append(len(data))
            
            P = Paragraph('<para>%s</para>' % item.ingredient.name,
                          styleSheet["Normal"])
            data.append(["%sg" % item.amount_gramm, P])
    
    # Set general table styles
    table_style = []
    table_style = [('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                   ('BOX', (0,0), (-1,-1), 0.25, colors.black)]
    
    # Set specific styles, e.g. background for title cells
    previous_marker = 0
    for marker in meal_markers:
        # Set background colour for headings
        table_style.append(('BACKGROUND', (0, marker), (-1, marker), colors.green))
        table_style.append(('BOX', (0, marker), (-1, marker), 1.25, colors.black))
        
        # Make the headings span the whole width
        table_style.append(('SPAN', (0, marker), (-1, marker)))

    
    t = Table(data, style = table_style)
    
    # Manually set the width of the columns
    t._argW[0] = 2 * cm


    # write the document and send the response to the browser
    elements.append(t)
    doc.build(elements)

    return response


# ************************
# Meal functions
# ************************

class MealForm(ModelForm):
    class Meta:
        model = Meal
        exclude=('plan',)

class MealItemForm(ModelForm):
    class Meta:
        model = MealItem
        exclude=('meal', 'order')

@login_required
def edit_meal(request, id, meal_id):
    """Form to add a meal to a plan
    """
    template_data = {}
    template_data['active_tab'] = 'nutrition'
    
    # Load the plan
    plan = get_object_or_404(NutritionPlan, pk=id, user=request.user)
    template_data['plan'] = plan
    
    # Load the meal
    meal = get_object_or_404(Meal, pk=meal_id)
    template_data['meal'] = meal
    
    if meal.plan != plan:
        return HttpResponseForbidden()
    
    
    # Process request
    if request.method == 'POST':
        meal_form = MealForm(request.POST, instance=meal)
        
        # If the data is valid, save and redirect
        if meal_form.is_valid():
            meal_item = meal_form.save(commit=False)
            meal_item.order = 1
            meal_item.save()
            
            return HttpResponseRedirect('/nutrition/%s/view/' % id)
    else:
        meal_form = MealForm(instance=meal)
    template_data['form'] = meal_form
    
    
    return render_to_response('edit_meal.html', 
                              template_data,
                              context_instance=RequestContext(request))
    


@login_required
def add_meal(request, id, meal_id=None):
    """Form to add a meal to a plan
    """
    template_data = {}
    template_data['active_tab'] = 'nutrition'
    
    # Load the plan
    plan = get_object_or_404(NutritionPlan, pk=id, user=request.user)
    template_data['plan'] = plan
    
    meal = Meal()
    meal.plan = plan
    meal.order = 1
    meal.save()
    
    return HttpResponseRedirect('/nutrition/%s/view/' % plan.id)

@login_required
def delete_meal(request, id):
    """Deletes the meal with the given ID
    """
    
    # Load the meal
    meal = get_object_or_404(Meal, pk=id)
    plan = meal.plan
    
    # Only delete if the user is the owner
    if plan.user == request.user:
        meal.delete()
        return HttpResponseRedirect('/nutrition/%s/view/' % plan.id)
    else:
        return HttpResponseForbidden()



# ************************
# Meal ingredient functions
# ************************

@login_required
def delete_meal_item(request, item_id):
    """Deletes the meal ingredient with the given ID
    """
    
    # Load the item
    item = get_object_or_404(MealItem, pk=item_id)
    plan = item.meal.plan
    
    # Only delete if the user is the owner
    if plan.user == request.user:
        item.delete()
        return HttpResponseRedirect('/nutrition/%s/view/' % plan.id)
    else:
        return HttpResponseForbidden()

@login_required
def edit_meal_item(request, id, meal_id, item_id=None):
    """Form to add a meal to a plan
    """
    template_data = {}
    template_data['active_tab'] = 'nutrition'
    
    # Load the plan
    plan = get_object_or_404(NutritionPlan, pk=id, user=request.user)
    template_data['plan'] = plan
    
    # Load the meal
    meal = get_object_or_404(Meal, pk=meal_id)
    template_data['meal'] = meal
    
    if meal.plan != plan:
        return HttpResponseForbidden()
    
    
    # Load the meal item
    if not item_id or item_id == 'None':
        meal_item = MealItem()
    else:
        meal_item = get_object_or_404(MealItem, pk=item_id)
        template_data['ingredient'] = meal_item.ingredient.id
        

    template_data['meal_item'] = meal_item
    
    # Check that javascript is activated This is used to hide the drop down list with the
    # ingredients and use the autocompleter version instead. This is not only nicer but also much
    # faster as the ingredient list from USDA is many thosand entries long.
    js_active = request.GET.get('js', False)
    template_data['js_active'] = js_active
    
    
    # Process request
    if request.method == 'POST':
        meal_form = MealItemForm(request.POST, instance=meal_item)
        
        # Pass the ingredient ID back to the template, this is originally set by the JQuery
        # autocompleter, in case of errors (max. gramms reached), we need to set the ID manually
        # so the user can simply submit again.
        template_data['ingredient'] = request.POST.get('ingredient', '')
        
        template_data['ingredient_searchfield'] = request.POST.get('ingredient_searchfield', '')
        
        
        # If the data is valid, save and redirect
        if meal_form.is_valid():
            meal_item = meal_form.save(commit=False)
            meal_item.meal = meal
            meal_item.order = 1
            meal_item.save()
            
            return HttpResponseRedirect('/nutrition/%s/view/' % id)
        #else:
        #    logger.debug(meal_form.errors)
    else:
        meal_form = MealItemForm(instance=meal_item)
    template_data['form'] = meal_form
    
    return render_to_response('edit_meal_item.html', 
                              template_data,
                              context_instance=RequestContext(request))

# ************************
# Ingredient functions
# ************************
def ingredient_overview(request):
    """Show an overview of all ingredients
    """
    language = load_language()
    
    template_data = {}
    template_data['active_tab'] = 'nutrition'
    
    #ingredients  = Ingredient.objects.filter(language = language.id)
    ingredients  = Ingredient.objects.all()
    
    template_data['ingredients'] = ingredients
    
    return render_to_response('ingredient_overview.html',
                              template_data,
                              context_instance=RequestContext(request))
    
def ingredient_view(request, id):
    template_data = {}
    template_data['active_tab'] = 'nutrition'
    
    ingredient = get_object_or_404(Ingredient, pk=id)
    template_data['ingredient'] = ingredient
    
    return render_to_response('view_ingredient.html', 
                              template_data,
                              context_instance=RequestContext(request))

@permission_required('nutrition.delete_ingredient')
def delete_ingredient(request, id):
    """Deletes the ingredient with the given ID
    """
    # Load the meal and redirect
    ingredient = get_object_or_404(Ingredient, pk=id)
    ingredient.delete()
    
    return HttpResponseRedirect('/nutrition/ingredient/overview/')

class IngredientForm(ModelForm):
    class Meta:
        model = Ingredient
        exclude=('language',)

@permission_required('nutrition.change_ingredient')
def ingredient_edit(request, id=None):
    """Edit view for an ingredient
    """
    
    template_data = {}
    template_data['active_tab'] = 'nutrition'
    
    # Load the ingredient
    if id:
        ingredient = get_object_or_404(Ingredient, pk=id)
        template_data['ingredient'] = ingredient
    else:
        ingredient = Ingredient()
    
    
    
    # Process request
    if request.method == 'POST':
        form = IngredientForm(request.POST, instance=ingredient)
        
        # If the data is valid, save and redirect
        if form.is_valid():
            language = load_language()
            
            ingredient = form.save(commit=False)
            ingredient.language = language
            ingredient.save()
            
            return HttpResponseRedirect('/nutrition/ingredient/view/%s' % ingredient.id)
    else:
        form = IngredientForm(instance=ingredient)
    template_data['form'] = form
    
    
    return render_to_response('edit_ingredient.html', 
                              template_data,
                              context_instance=RequestContext(request))


def ingredient_search(request):
    """Search for an exercise, return the result as a JSON list or as HTML page, depending on how
    the function was invoked
    """
    
    # Perform the search
    q = request.GET.get('term', '')
    ingredients = Ingredient.objects.filter(name__icontains = q )
    
    # AJAX-request, this comes from the autocompleter. Create a list and send it back as JSON
    if request.is_ajax():
        
        results = []
        for ingredient in ingredients:
            ingredient_json = {}
            ingredient_json['id'] = ingredient.id
            ingredient_json['name'] = ingredient.name
            ingredient_json['value'] = ingredient.name
            results.append(ingredient_json)
        data = json.dumps(results)
        
        # Return the results to the server
        mimetype = 'application/json'
        return HttpResponse(data, mimetype)
    
    # Usual search (perhaps JS disabled), present the results as normal HTML page
    else:
        template_data = {}
        template_data.update(csrf(request))
        template_data['ingredients'] = ingredients
        template_data['search_term'] = q
        return render_to_response('ingredient_search.html',
                                  template_data,
                                  context_instance=RequestContext(request))