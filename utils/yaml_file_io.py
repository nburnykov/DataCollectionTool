from yaml import load, dump
from typing import Optional, Union, List, Dict
import logging
import os

logger = logging.getLogger('main')


def yaml_load(file: str) -> Union[List, Dict]:

    try:
        with open(file) as data_file:
            data = load(data_file)
    except IOError:
        logger.error(f'Can\'t open file {file}')
        data = []
    if data is None:
        data = []
    return data


def yaml_dump(file: str, data: Union[List, Dict]) -> Union[List, Dict]:

    __writable_data = dump(data)
    writer(file, __writable_data)

    return __writable_data


def writer(file_name: str, data) -> bool:
    __dir = os.path.dirname(file_name)
    __result = False
    try:
        if not os.path.isdir(__dir):
            os.makedirs(__dir)
        with open(file_name, 'w') as data_file:
            data_file.write(data)
        __result = True
    except IOError:
        logger.error(f'Can\'t create file {file_name} to write data')
    finally:
        return __result