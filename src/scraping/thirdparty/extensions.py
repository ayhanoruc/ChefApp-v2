import json 
import copy 
# FUNCTIONS AND DATASTRUCTURES RELATED TO WEBSCRAPING VIA CHROME EXTENSIONS
recipe_websites = [
    "https://tasty.co",
    "https://www.allrecipes.com/recipes-a-z-6735880", # allrecipes.com: a-z
    "https://www.allrecipes.com", # allrecipes.com for unique categorical search
    "https://www.foodnetwork.com", # for recipe categories.
    "https://www.bbcgoodfood.com/recipes" # huge!!!
]


allrecipes_url_dict = {
"italian_maintag_urls" : [
    "https://www.allrecipes.com/recipes/16767/world-cuisine/european/italian/main-dishes/",

    "https://www.allrecipes.com/recipes/505/main-dish/pasta/spaghetti/",
    "https://www.allrecipes.com/recipes/250/main-dish/pizza/"
]
,
"italian_single_urls" : [
    "https://www.allrecipes.com/recipes/17551/world-cuisine/european/italian/drinks/",
    "https://www.allrecipes.com/recipes/1789/world-cuisine/european/italian/authentic/",
    "https://www.allrecipes.com/recipes/1790/world-cuisine/european/italian/soups-and-stews/",
    "https://www.allrecipes.com/recipes/1791/world-cuisine/european/italian/desserts/",
    "https://www.allrecipes.com/recipes/1793/world-cuisine/european/italian/appetizers/",
    "https://www.allrecipes.com/recipes/1800/world-cuisine/european/italian/salads/",
]
,
"mexican_maintag_urls" : [
  "https://www.allrecipes.com/recipes/1214/world-cuisine/latin-american/mexican/appetizers/",
  "https://www.allrecipes.com/recipes/1215/world-cuisine/latin-american/mexican/soups-and-stews/",
  "https://www.allrecipes.com/recipes/1217/world-cuisine/latin-american/mexican/desserts/",
  "https://www.allrecipes.com/recipes/17504/world-cuisine/latin-american/mexican/main-dishes/"

],
"mexican_single_urls" : [
  "https://www.allrecipes.com/recipes/1470/world-cuisine/latin-american/mexican/authentic/",
  "https://www.allrecipes.com/recipes/17513/world-cuisine/latin-american/mexican/salads/",
  "https://www.allrecipes.com/recipes/1216/world-cuisine/latin-american/mexican/main-dishes/burritos/"
]
,
"chineese_maintag_urls" : [
  "https://www.allrecipes.com/recipes/17135/world-cuisine/asian/chinese/main-dishes/",

],
"chineese_single_urls" : [
  "https://www.allrecipes.com/recipes/1899/world-cuisine/asian/chinese/appetizers/",
  "https://www.allrecipes.com/recipes/1900/world-cuisine/asian/chinese/soups-and-stews/",
  "https://www.allrecipes.com/recipes/22838/world-cuisine/asian/chinese/main-dishes/beef/",
  "https://www.allrecipes.com/recipes/1902/world-cuisine/asian/chinese/main-dishes/chicken/",
  "https://www.allrecipes.com/recipes/1901/world-cuisine/asian/chinese/main-dishes/pork/",
  "https://www.allrecipes.com/recipes/1903/world-cuisine/asian/chinese/main-dishes/seafood/"
],


"middle_eastern_single_urls" : [
  "https://www.allrecipes.com/recipes/15937/world-cuisine/middle-eastern/persian/",
  "https://www.allrecipes.com/recipes/1824/world-cuisine/middle-eastern/lebanese/",
  "https://www.allrecipes.com/recipes/1825/world-cuisine/middle-eastern/turkish/",
  "https://www.allrecipes.com/recipes/1826/world-cuisine/middle-eastern/israeli/",
  "https://www.allrecipes.com/recipes/16704/healthy-recipes/mediterranean-diet/"
],


"japanese_single_urls" : [
  "https://www.allrecipes.com/recipes/17490/world-cuisine/asian/japanese/appetizers/",
    "https://www.allrecipes.com/recipes/17491/world-cuisine/asian/japanese/main-dishes/",
    "https://www.allrecipes.com/recipes/17492/world-cuisine/asian/japanese/soups-and-stews/"
],

"low_carb_maintag_urls" : [
  "https://www.allrecipes.com/recipes/1591/healthy-recipes/low-carb/main-dishes/",

],
"low_carb_single_urls" : [
  "https://www.allrecipes.com/recipes/1594/healthy-recipes/low-carb/side-dishes/",
  "https://www.allrecipes.com/recipes/1595/healthy-recipes/low-carb/appetizers/",
  "https://www.allrecipes.com/recipes/1596/healthy-recipes/low-carb/desserts/",

],

"breakfast_maintag_urls" : [
  "https://www.allrecipes.com/recipes/143/breakfast-and-brunch/drinks/",
  "https://www.allrecipes.com/recipes/144/breakfast-and-brunch/breakfast-casseroles/",
  "https://www.allrecipes.com/recipes/145/breakfast-and-brunch/cereals/",
  "https://www.allrecipes.com/recipes/147/breakfast-and-brunch/crepes/",
  "https://www.allrecipes.com/recipes/148/breakfast-and-brunch/eggs/",
  "https://www.allrecipes.com/recipes/149/breakfast-and-brunch/french-toast/",
  "https://www.allrecipes.com/recipes/151/breakfast-and-brunch/pancakes/",
  "https://www.allrecipes.com/recipes/152/breakfast-and-brunch/potatoes/"],

"breakfast_single_urls" : [
  "https://www.allrecipes.com/recipes/1316/breakfast-and-brunch/waffles/",
  "https://www.allrecipes.com/recipes/17766/breakfast-and-brunch/breakfast-cookies/"
],


"drinks_maintag_urls" : [
  "https://www.allrecipes.com/recipes/134/drinks/coffee/",
  "https://www.allrecipes.com/recipes/136/drinks/punch/",
  "https://www.allrecipes.com/recipes/137/drinks/shakes-and-floats/",
  "https://www.allrecipes.com/recipes/138/drinks/smoothies/"
],


"vegan_single_urls" : [
  "https://www.allrecipes.com/recipes/16570/everyday-cooking/vegan/soups-and-stews/",
  "https://www.allrecipes.com/recipes/1661/everyday-cooking/vegan/main-dishes/",
  "https://www.allrecipes.com/recipes/1663/everyday-cooking/vegan/side-dishes/",
  "https://www.allrecipes.com/recipes/1664/everyday-cooking/vegan/desserts/",
  "https://www.allrecipes.com/recipes/17093/everyday-cooking/vegan/breakfast-and-brunch/"

],

"gluten_free_single_urls" : [
  "https://www.allrecipes.com/recipes/1696/healthy-recipes/gluten-free/main-dishes/",
  "https://www.allrecipes.com/recipes/1697/healthy-recipes/gluten-free/appetizers/",
  "https://www.allrecipes.com/recipes/1698/healthy-recipes/gluten-free/side-dishes/",
  "https://www.allrecipes.com/recipes/1755/healthy-recipes/gluten-free/bread/",
  "https://www.allrecipes.com/recipes/17685/healthy-recipes/gluten-free/breakfast-and-brunch/"
],

"gluten_free_maintag_urls" : [
  "https://www.allrecipes.com/recipes/1695/healthy-recipes/gluten-free/desserts/"
],

"healthy_single_urls" : [
  "https://www.allrecipes.com/recipes/12155/healthy-recipes/snacks/",
  "https://www.allrecipes.com/recipes/1346/healthy-recipes/salads/",
  "https://www.allrecipes.com/recipes/1319/healthy-recipes/appetizers/",
  "https://www.allrecipes.com/recipes/1321/healthy-recipes/side-dishes/",
  "https://www.allrecipes.com/recipes/15587/healthy-recipes/low-glycemic-impact/",
  "https://www.allrecipes.com/recipes/16375/healthy-recipes/desserts/"

],
"healthy_maintag_urls" : [
  "https://www.allrecipes.com/recipes/1231/healthy-recipes/low-fat/",
  "https://www.allrecipes.com/recipes/1232/healthy-recipes/low-calorie/",
  "https://www.allrecipes.com/recipes/738/healthy-recipes/dairy-free/",
  "https://www.allrecipes.com/recipes/22959/healthy-recipes/keto-diet/",
  "https://www.allrecipes.com/recipes/1320/healthy-recipes/main-dishes/",
  "https://www.allrecipes.com/recipes/15334/healthy-recipes/breakfast-and-brunch/"
],
"dinner_maintag_urls" : [
  "https://www.allrecipes.com/recipes/475/meat-and-poultry/beef/steaks/",
  "https://www.allrecipes.com/recipes/476/everyday-cooking/cooking-for-two/"
],
"dinner_single_urls" : [
  "https://www.allrecipes.com/recipes/15054/everyday-cooking/cooking-for-one/quick-and-easy/",
  "https://www.allrecipes.com/recipes/22992/everyday-cooking/sheet-pan-dinners/"

],

"desserts_maintag_urls" : [
  "https://www.allrecipes.com/recipes/1557/desserts/chocolate/",
  "https://www.allrecipes.com/recipes/15840/desserts/crisps-and-crumbles/",
  "https://www.allrecipes.com/recipes/17100/desserts/frostings-and-icings/",
  "https://www.allrecipes.com/recipes/17140/desserts/fruit-desserts/",
  "https://www.allrecipes.com/recipes/17203/desserts/specialty-desserts/",
  "https://www.allrecipes.com/recipes/276/desserts/cakes/",
  "https://www.allrecipes.com/recipes/363/desserts/custards-and-puddings/"
]
}


# SITEMAP TEMPLATES

main_tag_sitemap = {
  "sitemap":
    {"_id":"italian_maindishes","startUrl":["https://www.allrecipes.com/recipes/16767/world-cuisine/european/italian/main-dishes/"],
    "selectors":[{"id":"sublink","linkType":"linkFromHref","multiple":"true","parentSelectors":["_root"],"selector":"a.taxonomy-nodes__link","type":"SelectorLink"},{"id":"sub_category","multiple":"false","parentSelectors":["sublink"],"regex":"","selector":"h1","type":"SelectorText"},{"id":"card","linkType":"linkFromHref","multiple":"true","parentSelectors":["sublink"],"selector":".tax-sc__recirc-list a","type":"SelectorLink"},{"id":"recipe_name","multiple":"false","parentSelectors":["card"],"regex":"","selector":"h1","type":"SelectorText"},{"extractAttribute":"","id":"recipe_details_table","parentSelectors":["card"],"selector":"div.mntl-recipe-details__content","type":"SelectorGroup"},{"extractAttribute":"","id":"ingredients","parentSelectors":["card"],"selector":"ul.mntl-structured-ingredients__list","type":"SelectorGroup"},{"extractAttribute":"","id":"recipe_directions","parentSelectors":["card"],"selector":".mntl-sc-block-group--LI p","type":"SelectorGroup"},{"extractAttribute":"","id":"recipe_tags","parentSelectors":["card"],"selector":".mntl-breadcrumbs__link span","type":"SelectorGroup"},{"extractAttribute":"","id":"recipe_nutrition_details","parentSelectors":["card"],"selector":"tbody.mntl-nutrition-facts-summary__table-body","type":"SelectorGroup"}]}
}

single_url_sitemap = {
  "sitemap":
    {"_id":"italian_chichen","startUrl":["https://www.allrecipes.com/recipes/1796/world-cuisine/european/italian/main-dishes/chicken/"],"selectors":[{"id":"sub_category","multiple":"false","parentSelectors":["_root"],"regex":"","selector":"h1","type":"SelectorText"},{"id":"card","linkType":"linkFromHref","multiple":"true","parentSelectors":["_root"],"selector":".tax-sc__recirc-list a","type":"SelectorLink"},{"id":"recipe_name","multiple":"false","parentSelectors":["card"],"regex":"","selector":"h1","type":"SelectorText"},{"extractAttribute":"","id":"recipe_details_table","parentSelectors":["card"],"selector":"div.mntl-recipe-details__content","type":"SelectorGroup"},{"extractAttribute":"","id":"recipe_ingredients","parentSelectors":["card"],"selector":"ul.mntl-structured-ingredients__list","type":"SelectorGroup"},{"extractAttribute":"","id":"recipe_directions","parentSelectors":["card"],"selector":"p.mntl-sc-block","type":"SelectorGroup"},{"extractAttribute":"","id":"recipe_tags","parentSelectors":["card"],"selector":".mntl-breadcrumbs__link span","type":"SelectorGroup"},{"extractAttribute":"","id":"recipe_nutrition_details","parentSelectors":["card"],"selector":"table.mntl-nutrition-facts-summary__table","type":"SelectorGroup"}]}
}

# TEMPLATE GENERATOR :
# Input: Dictionary of URL lists with names like "{tag}_maintag_urls" or "{tag}_single_urls"


# Initialize an empty list to store the sitemap templates
sitemap_templates = []

# Iterate over the input URL lists and generate sitemap templates
for list_name, url_list in allrecipes_url_dict.items():
    # Determine the type of template based on the list_name
    if "maintag" in list_name:
        template = main_tag_sitemap.copy()
    elif "single" in list_name:
        template = single_url_sitemap.copy()
    else:
        print(f"Unknown template type for list '{list_name}'")
        continue

    # Extract the tag name from the list_name
    tag = list_name.split("_")[0]
    first_part_sitemap_id = tag
    # Iterate through each URL in the list
    for url in url_list:
        # Extract the second part of sitemap_id from the URL
        try:
            second_part_sitemap_id = url.split('/')[-2]
            print(second_part_sitemap_id)
        except:
            print(tag, ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>", url)
            continue

        # Generate the first part of sitemap_id from the tag
        

        # Combine the first and second parts to create the sitemap_id
        sitemap_id = f"{first_part_sitemap_id}_{second_part_sitemap_id}"

        # Create a new template for each URL
        new_template = copy.deepcopy(template)

        # Update sitemap_id and entry_url in the new template
        new_template["sitemap"]["_id"] = sitemap_id
        new_template["sitemap"]["startUrl"] = [url]
        print(new_template)
        print(url)

        # Append the generated sitemap template to the list
        sitemap_templates.append(new_template)

# Print the generated sitemap templates
output_file = r"C:\Users\ayhan\Desktop\ChefApp\src\templates\sitemap_templates.json"

with open(output_file, "w") as f:
    json.dump(sitemap_templates, f, indent=2)

print(f"Sitemap templates saved to {output_file}")

