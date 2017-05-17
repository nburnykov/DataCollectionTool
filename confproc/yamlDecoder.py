import yaml


def yamlload(file):

    with open(file) as data_file:
        data = yaml.load(data_file)
    return data
