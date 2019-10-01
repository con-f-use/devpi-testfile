#!/usr/bin/python3
import sys
import json
from pprint import pprint


def gen_dict_extract(key, var):
    if hasattr(var, "items"):
        for k, v in var.items():
            if k == key:
                yield v
            if isinstance(v, dict):
                for result in gen_dict_extract(key, v):
                    yield result
            elif isinstance(v, list):
                for d in v:
                    for result in gen_dict_extract(key, d):
                        yield result


if __name__ == "__main__":
    with open(sys.argv[1], "rU") as fl:
        data = json.load(fl)
    pprint(data)
    for itm in gen_dict_extract("installpkg", data):
        pprint(itm)
