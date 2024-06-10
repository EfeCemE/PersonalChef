import pandas as pd
import json

def load_dishes_from_json(training_data_file):
    with open(training_data_file, 'r') as file:
        ingredients_data = json.load(file)
    return ingredients_data

ingredients_data = load_dishes_from_json('train.json')
df = pd.DataFrame(ingredients_data)

#example
def filter_user_input(user_input, valid_options):
    return [item.strip() for item in user_input.split(',') if item.strip() in valid_options]

def get_unique_ingredients(ingredients_data):

    all_ingredients = [ingredient for sublist in df['ingredients'] for ingredient in sublist]
    unique_ingredients = list(set(all_ingredients))
    return unique_ingredients


def get_recipe_recommendations(ingredients, exclude_ingredients, cuisine):
    matching_dishes = df[df['cuisine']] == cuisine
    matching_dishes = matching_dishes[matching_dishes['ingredients'].apply(lambda x: set(ingredients).issubset(set(x)))]

    if exclude_ingredients:
        for exclude_ingredient in exclude_ingredients:
            matching_dishes = matching_dishes[~matching_dishes['ingredients'].apply(lambda x: exclude_ingredient in x)]
    
    if not matching_dishes.empty:
        return matching_dishes['id'].iloc[0]
    else:
        return "No matching dishes"