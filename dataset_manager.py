import pandas as pd
import json

def load_dishes_from_csv(csv_file):
    return pd.read_csv(csv_file)

df = load_dishes_from_csv('recipes.csv')

#example
def filter_user_input(user_input, valid_options):
    return [item.strip() for item in user_input.split(',') if item.strip() in valid_options]

def get_recipe_recommendations(ingredients, exclude_ingredients, cuisine, max_total_time):
    
    # delete this line only for testing
    #return "1. boil pasta with sauce then add oil in pan add sauce cook sauce for 5 minutes and boiled pasta enjoy"

    matching_dishes = df[df['cuisine_path'].str.contains(cuisine, case=False)]
    #matching_dishes = matching_dishes[matching_dishes['ingredients'].apply(lambda x: set(ingredients).issubset(set(literal_eval(x))))]
    
    def has_required_ingredients(dish_ingredients):
        dish_ingredients_list = json.loads(dish_ingredients)
        return all(ingredient in dish_ingredients_list for ingredient in ingredients)
    
    matching_dishes = matching_dishes[matching_dishes['ingredients'].apply(has_required_ingredients)]
    
    if exclude_ingredients:
        def exclude_undesired_ingredients(dish_ingredients):
            dish_ingredients_list = json.loads(dish_ingredients)
        
            return not any(exclude_ingredient in dish_ingredients_list for exclude_ingredient in exclude_ingredients)
        #for exclude_ingredient in exclude_ingredients:
        #    matching_dishes = matching_dishes[~matching_dishes['ingredients'].apply(lambda x: exclude_ingredient in literal_eval(x))]
        
        matching_dishes = matching_dishes[matching_dishes['ingredients'].apply(exclude_undesired_ingredients)]
    
    if max_total_time is not None:
        matching_dishes = matching_dishes[matching_dishes['total_time'] <= max_total_time]
    
    if not matching_dishes.empty:
        return matching_dishes[['recipe_name', 'prep_time', 'cook_time', 'total_time', 'servings', 'ingredients', 'directions', 'cuisine_path']].to_dict(orient='records')
    else:
        return "No matching dishes found."