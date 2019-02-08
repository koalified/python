import os
import pytest

from koalified.schema import Schema

EXAMPLE_SCHEMA = """
name+:
    - match [A-z]
    - str longest=4:int cut=true:bool
age: int minimum=1:int maximum=10:int
contact+!:
    phone:
       - int!=
       - str=
    fax: str
"""


def test_load_schema():
    with pytest.raises(ValueError):
        Schema()
    with pytest.raises(ValueError):
        Schema(text=EXAMPLE_SCHEMA, uri='google.com')
    schema = Schema(text=EXAMPLE_SCHEMA, precompile=True)
    schema = Schema(uri='./examples/example_schema.yaml', precompile=True)
    schema = Schema(uri='https://raw.github.com/domaintools/koalified_python/develop/examples/example_schema.yaml')
    schema = Schema(text=EXAMPLE_SCHEMA, fail_fast=False, score_fields=True, explain=True, precompile=True)
    schema = Schema(uri='./examples/example_schema2.yaml')

    abspath = os.path.abspath(os.path.dirname(__file__))
    schema = Schema(uri=abspath + '/../examples/example_schema2.yaml')

    schema = Schema(text=EXAMPLE_SCHEMA)
    schema.compiled()
    assert schema({'contact': [{'phone': '410'}]})
