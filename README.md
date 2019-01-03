![koalified](https://raw.github.com/domaintools/koalified_python/develop/artwork/logo.png)
===================

[![PyPI version](https://badge.fury.io/py/koalified.svg)](http://badge.fury.io/py/koalified)
[![Build Status](https://travis-ci.org/DomainTools/koalified_python.svg?branch=master)](https://travis-ci.org/DomainTools/koalified_python)
[![Coverage Status](https://coveralls.io/repos/DomainTools/koalified_python/badge.svg?branch=master&service=github)](https://coveralls.io/github/DomainTools/koalified_python?branch=master)
[![License](https://img.shields.io/github/license/mashape/apistatus.svg)](https://pypi.python.org/pypi/koalified/)
[![Join the chat at https://gitter.im/domaintools/koalified_python](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/koalified_python?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

# Koalified
## for when truth is a little fuzzy.

As engineers, we would love it if all our source data was of perfect quality and structured identically. However, this is not something we always have control over. Koalified is built for the cases where you don't have control over the source data but want to capture as much data as possible, while getting a sense of the quality of that data versus your known ideal.

Koalified allows you to specify:
- What data must contain
- What data can contain
- What data ideally contains

All within one single and concise schema definition.

It also has built-in support for pulling schemas from a central schema service or service system and composing schemas together.

Koalified is built on top of a YAML base with the following symbol based rules:

* `!` = required
* `?` = fully optional (won't impact score)
* `+` = multiple
* `~` = weight, needs to be followed by a number (name~20). The default weight is 1.
* `@` = extend schema (provide URI of schema to extend)
* `&` = include/nest schema (provide URI of schema to include)
* `=` = allow validator to mutate the given data
* `**` = a field name that represents all extra undefined keys in the input data. Can be used to include and normalize extra data than what is strictly defined. All extra data is

Using koalified
===============

Creating a schema:
```python
from koalified.schema import Schema

schema = Schema(text="""
name:
    - match [A-z]
    - str= longest=10:int cut=true:bool
age: int minimum=18:int maximum=120:int
contact+!:
    phone!:
       - phone=
    fax:
       - phone=""")
```

You can either pass in the YAML data directly, as shown above, or pass in an http or local disc location.

When creating the schema object can specify the following instantiation arguments:

* **fail_fast**: (default: `True`) if set to `True`, will fail after first requirement is not met, and raise only that exception. If set to `False`, will collect and return all encountered errors.
* **score_fields**: (default: `False`) if set to `True`, a score will be returned for all individual fields in addition to the overall score.
* **explain**: (default: `False`) if set to `True`, a detailed explanation behind the scoring will be returned.
* **allow_imports**: (default: `True`) if set to `True`, the schema will be allowed to import and extend other schemas either locally or over http.
* **precompile**: (default: `False`) if set to `True`, the schema will immediately be compiled upon instantiation of the class. If set to `False`, the schema is compiled upon it's first use.
* **supported_types**: (default: `None`) a dictionary of type_names to callables that will cast into the given type or raise an exception. Can be used to add custom schema types.

Using a schema:
```python
schema({'name': 'timothy', 'age': 29, 'contact': [{'fax':'1800phonenumber', 'phone': '5555555555'}]}) == \
       {'__metadata__': {'schema_version': '4f5f88bc', 'score': 0.75}, 'age': 29, 'contact': [{'fax': '1800phonenumber', 'phone': '5555555555'}], 'name': 'timothy'}
```


Installing koalified
===================

Installing koalified is as simple as:

```bash
pip3 install koalified --upgrade
```

Ideally, within a virtual environment.


Why koalified?
===================

Koalified was built to help solve the case where the source of data can't be fully trusted but needs to be stored.
It allows specifying what should be, what can be, and what must be, in one concise schema definition.

--------------------------------------------

Thanks and I hope you find koalified helpful!

~Timothy Crosley
