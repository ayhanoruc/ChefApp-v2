import yaml

prompt_file = r"C:\Users\ayhan\Desktop\ChefApp\src\handler_api\prompts.yaml"

#read yaml file

with open(prompt_file) as f:
    prompts = yaml.load(f, Loader=yaml.FullLoader)

print(prompts['RECIPE_DETAILS_FORMATTER'])