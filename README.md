# setuphelpers

Helper functions for writing setup.py's.

## Helper functions

`setuphelpers` provides the following:

### `git_version`

Use to supply your package's version string from git. If the latest commit is
tagged, the version will be that tag. If it is not tagged, it will be the last
version + 1 minor/patch version .devN number of commits since last tag. If
building off a branch other than master, the branch name is used as a local
version identifier.

Examples: `0.0.1`, `0.0.2.dev1`, `0.0.2.dev1+featureX`

```python
from setuptools import setup
from setuphelpers import git_version

setup(name="my_thing", version=git_version())
```

### `long_description`

Use to fill in the long_description field with the contents of your README.
If no README is found, will fallback to the docstring of your setup.py.

```python
from setuptools import setup
from setuphelpers import long_description

setup(name="my_thing", version="1.0", long_description=long_description())
```

### `find_version`

Used to find the value assigned to \_\_version\_\_ in the specified filepath.

```python
from setuptools import setup
from setuphelpers import find_version

setup(name="my_thing", version=find_version("my_thing/__init__.py"))
```

### `test_command`

Used to build a test command class for running unit tests with
`python setup.py test`. Default support is for py.test, but nose and unittest
are also both possible. The return from `test_command` can be passed to `cmdclass`.

Note that the `tests_require` dependancies still need to be provided, including
coverage, if you're using it (plus whatever else you need to test with).


```python
from setuptools import setup
from setuphelpers import find_version

setup(
    name="my_thing",
    version="1.0",
    tests_require=["pytest", "pytest-cov"],
    cmdclass=test_command(cover="my_thing"),
)
```

## A note on `setup_requires`

You can (and should) put `setuphelpers` in the `setup_requires` argument of
your setup.py. But you also need to be careful to avoid dependency problems
during build. To accomplish this, you can use this pattern (for each/any of the
used functions):

```python
from setuptools import setup
try:
    from setuphelpers import (
        find_version,  # not used, but for completeness
        git_version,
        long_description,
        test_command,
    )
except ImportError:
    find_version = lambda x: "0.0.0"
    git_version = lambda: "0.0.0"
    long_description = lambda: __doc__
    test_command = lambda **_: {}


setup(
    name="my_thing",
    version=git_version(),  # find_version("my_thing/__init__.py"),
    description=long_description(),
    tests_require=["pytest", "pytest-cov"],
    setup_requires=["setuphelpers"],
    cmdclass=test_command(cover="my_thing"),
)
```

Now `python setup.py install` should pull in `setuphelpers` if it's missing,
and re-exec itself to fill in the arguments as expected. You need to manually
avoid both the `ImportError` and the `NameError` though, so mock callables need
to be created in the case of missing `setuphelpers`.
