import pandas as pd
import json

matched_ingredient = []
unmatches = 999999999999

def load_dishes_from_csv(csv_file):
    return pd.read_csv(csv_file)

df = load_dishes_from_csv('recipes.csv')

#example
def filter_user_input(user_input, valid_options):
    return [item.strip() for item in user_input.split(',') if item.strip() in valid_options]


#To store ranked ingredient list and rank score
matched_ingredient = []
unmatches = 999999999999



def get_recipe_recommendations(ingredients, exclude_ingredients, cuisine, max_total_time):
    
    initial_filtered_df = df[df['cuisine_path'].str.lower().str.contains(cuisine.lower(), na=False)]
    filtered_df = initial_filtered_df[~initial_filtered_df['ingredients'].isin(exclude_ingredients)]
    
    #Method to filter reciepes based on ingredients and excluded ingredients
    def check_match(recipe_ingredients):
        if type(recipe_ingredients) != str:
            return False

        split_recipe_ingredients = recipe_ingredients.split(',')
        split_recipe_ingredients = [x.lower() for x in split_recipe_ingredients]

        matches = 0
        #if a user inputed ingredient is in reciepe we increase the match count
        #if a user inputed excluded_ingredient is in reciepe we decrease the match count
        for split_ingredient in split_recipe_ingredients:
            if split_ingredient == '':
                continue
            for i in ingredients:
                if i.lower() in split_ingredient:
                #print( i.lower() + '**********' + split_ingredient)
                    matches += 1
            for i in exclude_ingredients:
                if i.lower() in split_ingredient:
                    print( i.lower() + '**********' + split_ingredient)
                    matches -= 1
        

        global unmatches
        global matched_ingredient
        #if matches are above a certain threshold we consider only those recipe and rank them
        if matches / len(ingredients)  >= 1:
            match_score = len(split_recipe_ingredients) - matches
            if match_score < unmatches:
                unmatches = match_score
                matched_ingredient = recipe_ingredients
            print(matches)
            return True
        #if matches are below a certain threshold we do not consider
        else:
            return False

    # Filter DataFrame based on match threshold
    mask = filtered_df['ingredients'].apply(check_match)
    ingriedient_filtered_df = filtered_df[mask]

    print(matched_ingredient)
    print(unmatches)

    matching_dishes = ingriedient_filtered_df[ingriedient_filtered_df['ingredients'].str.contains(matched_ingredient, regex = False)]
    print(matching_dishes)
    
    matching_dishes_new = matching_dishes
    if max_total_time is not None:
        matching_dishes_new = matching_dishes[matching_dishes['total_time'] <= max_total_time]
    
    if not matching_dishes_new.empty:
        matching_dishes = matching_dishes_new
    if not matching_dishes.empty:
        reciepe = "Recipe Name : "  .join(str(matching_dishes['recipe_name'])) .join( 
                  "\n") + "Preparation Time: "  .join(str(matching_dishes['prep_time'])) .join(
                  "\n") + "Cook Time: "  .join(matching_dishes['cook_time']) .join(
                  "\n") + "Serving: "  .join(str(matching_dishes['servings'])) .join(
                  "\n") + "Ingredients  :"  "\n".join(matching_dishes['ingredients']) .join(
                  "\n") + "Instruction :"  "\n".join(matching_dishes['directions'])
        return reciepe
    else:
        return "No matching dishes found."