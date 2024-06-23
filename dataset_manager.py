import pandas as pd

def load_dishes_from_csv(csv_file):
    return pd.read_csv(csv_file)

df = load_dishes_from_csv('recipes.csv')

#example
def filter_user_input(user_input, valid_options):
    return [item.strip() for item in user_input.split(',') if item.strip() in valid_options]

def get_recipe_recommendations(ingredients, exclude_ingredients, cuisine, max_total_time):
    
    # delete this line only for testing
    return "1. boil pasta with sauce then add oil in pan add sauce cook sauce for 5 minutes and boiled pasta enjoy"

    matching_dishes = df[df['cuisine_path'].str.contains(cuisine, case=False)]
    matching_dishes = matching_dishes[matching_dishes['ingredients'].apply(lambda x: set(ingredients).issubset(set(eval(x))))]

    if exclude_ingredients:
        for exclude_ingredient in exclude_ingredients:
            matching_dishes = matching_dishes[~matching_dishes['ingredients'].apply(lambda x: exclude_ingredient in eval(x))]
    
    if max_total_time is not None:
        matching_dishes = matching_dishes[~matching_dishes['ingredients'].apply(lambda x: exclude_ingredient in eval(x))]
    
    if not matching_dishes.empty:
        return matching_dishes[['recipe_name', 'prep_time', 'cook_time', 'total_time', 'servings', 'ingredients', 'directions', 'cuisine_path']].to_dict(orient='records')
    else:
        return "No matching dishes found."