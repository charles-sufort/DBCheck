import json
import sys
from pprint import pprint


if __name__ == "__main__":
    name = sys.argv[1]
    path = "tmp/" + name
    with open(path,"r") as fo:
        R = json.load(fo)
        pprint(R)



