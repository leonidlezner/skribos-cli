import yaml

class Download():
    def __init__(self, dict_entry):
        print(dict_entry)

with open('skribos.yml') as file:
    recipe = yaml.load(file, Loader=yaml.Loader)

    if 'downloads' in recipe:
        if isinstance(recipe['downloads'], list):
            downloads = list(map(lambda d: Download(d), recipe['downloads']))
        else:
            downloads = None
    else:
        downloads = None

    print(downloads)
