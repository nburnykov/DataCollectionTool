import json
import yaml

from pprint import pprint


def loadjson(file='..\\decisionTreeSNMP.json'):
    with open(file) as data_file:
        data = json.load(data_file)
    return data

s = loadjson()

with open('decisionTreeCLI.yaml', 'w') as f:
    f.write(yaml.dump(s))