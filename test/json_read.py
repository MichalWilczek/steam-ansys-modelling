import json
from collections import namedtuple

with open('input.json') as json_file:
    data = json.load(json_file, object_hook=lambda d: namedtuple('CableInput', d.keys())(*d.values()))
    print(type(data))
    print(data)
