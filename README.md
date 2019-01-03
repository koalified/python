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

[![koalified Example](https://raw.github.com/domaintools/koalified_python/develop/artwork/example.gif)](https://github.com/domaintools/koalified_python/blob/develop/examples/example.py)


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
