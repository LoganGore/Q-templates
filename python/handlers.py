import json


def handle_file(x):
    # This is where you'd have more complicated logic for a handler on a file drop!
    out = json.loads(x)
    print(out["fileAdded"]["name"])
    return out["fileAdded"]["name"]
