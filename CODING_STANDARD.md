Coding Standard
=========

Any submission to this project should closely follow the
[PEP 8](https://www.python.org/dev/peps/pep-0008/) coding guidelines.
To ensure a consistent format beyond PEP8, code should be linted with
[black](https://github.com/ambv/black), with lines can be up to 100
characters long.  Imports should be sorted with
[isort](https://github.com/timothycrosley/isort).


Suggested commands before sending a PR:

```shell
$ black -l 100 .
$ isort . -rc -m 3 -tc -fgw 0 -up -w 100
```
