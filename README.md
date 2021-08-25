# Stubmaker

Stubmaker is an easy-to-use tool for generating [python stubs](https://www.python.org/dev/peps/pep-0484/#stub-files).

Requirements
------------
- Stubmaker is to be run under Python 3.7.4+
- No side effects during module imports
- Must contain `__all__` (this restriction will be removed in upcomming releases)

How to install
----------
```bash
pip install stubmaker
stubmaker --help
```

Usage example
-------------

Imagine you have a package with the following structure:

```
package
-> __init__.py
```

Contents of `__init__.py`:
```python
__all__ = ['sleep_for']
from time import sleep


def some_decorator(func):
    return func


@some_decorator
def sleep_for(amount: float) -> None:
    sleep(amount)
```

There is a script that calls `sleep_for` method but passes wrong arguments:
```python
from package import sleep_for

sleep_for(123, 123)
```

Due to dynamic nature of decorators static analysers (such as mypy) may not raise an error while checking the script:
```bash
>> mypy __main__.py

Success: no issues found in 1 source file
```

Stubs exist to help you! Stubmaker will provide stubs for your package so that its users can find the error using mypy:
```bash
>> stubmaker --module-root package --src-root <path to package>/package --output-dir <path to package>/package
>> mypy __main__.py

__main__.py:3: error: Too many arguments for "sleep_for"
Found 1 error in 1 file (checked 1 source file)
```

License
-------
© YANDEX LLC, 2020-2021. Licensed under the Apache License, Version 2.0. See LICENSE file for more details.
