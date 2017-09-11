from yaml import load, dump
from typing import Optional, Union, List, Dict
import logging

logger = logging.getLogger('main')


def yamlload(file: str) -> Union[List, Dict]:

    try:
        with open(file) as data_file:
            data = load(data_file)
    except IOError:
        logger.error(f'Can\'t open file {file}')
        data = []
    if data is None:
        data = []
    return data


def yamldump(file: str, data: Union[List, Dict]) -> Union[List, Dict]:

    with open(file, 'w') as data_file:
        ddata = dump(data)
        data_file.write(ddata)
    return ddata
