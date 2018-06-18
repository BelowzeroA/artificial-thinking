import json
from json import JSONEncoder


class CustomEncoder(JSONEncoder):
    def default(self, o):
        return o.serialize()


def json_serialize(value):
    return json.dumps(value, cls=CustomEncoder)