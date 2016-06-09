setuphelpers
============

Helper functions for writing setup.py's.

|Build Status| |Coverage Status| |Version| |Download format| |Downloads
this month| |Development Status| |License|

Helper functions
----------------

``setuphelpers`` provides the following:

``git_version``
~~~~~~~~~~~~~~~

Use to supply your package's version string from git. If the latest
commit is tagged, the version will be that tag. If it is not tagged, it
will be the last version + 1 minor/patch version .devN number of commits
since last tag. If building off a branch other than master, the branch
name is used as a local version identifier.

Examples: ``0.0.1``, ``0.0.2.dev1``, ``0.0.2.dev1+featureX``

.. code:: python

    from setuptools import setup
    from setuphelpers import git_version

    setup(name="my_thing", version=git_version())

Note that you cannot deploy a sdist package using ``git_version``, due
to needing access to ``.git``. But please don't start including
``.git``'s in your packages. There is a pattern you can use to have
``git_version`` write out to a file to include, but I would argue that
there's not a need to do that, as it's already included in the written
package metadata anyway (wheels > \*). But if you must:

.. code:: python

    import os
    import io
    from setuptools import setup
    from setuphelpers import git_version
    from setuphelpers import find_version

    # VER_FILE should not exist in your checked in source
    VER_FILE = os.path.join("my_thing", "__version__.py")
    if os.path.isfile(VER_FILE):
        # this should only be run during rebuilding a sdist package
        VERSION = find_version(VER_FILE)
    else:
        # this should be run only during the actual packaging
        VERSION = git_version()
        with io.open(VER_FILE, "w", encoding="utf-8") as openversion:
            openversion.write('__version__ = "{}"'.format(VERSION))

    setup(name="my_thing", version=VERSION)

``long_description``
~~~~~~~~~~~~~~~~~~~~

Use to fill in the long\_description field with the contents of your
README. If no README is found, will fallback to the docstring of your
setup.py.

.. code:: python

    from setuptools import setup
    from setuphelpers import long_description

    setup(name="my_thing", version="1.0", long_description=long_description())

``find_version``
~~~~~~~~~~~~~~~~

Used to find the value assigned to \_\_version\_\_ in the specified
filepath.

.. code:: python

    from setuptools import setup
    from setuphelpers import find_version

    setup(name="my_thing", version=find_version("my_thing/__init__.py"))

``test_command``
~~~~~~~~~~~~~~~~

Used to build a test command class for running unit tests with
``python setup.py test``. Default support is for py.test, but nose and
unittest are also both possible. The return from ``test_command`` can be
passed to ``cmdclass``.

Note that the ``tests_require`` dependancies still need to be provided,
including coverage, if you're using it (plus whatever else you need to
test with).

.. code:: python

    from setuptools import setup
    from setuphelpers import test_command

    setup(
        name="my_thing",
        version="1.0",
        tests_require=["pytest", "pytest-cov"],
        cmdclass=test_command(cover="my_thing"),
    )

A note on ``setup_requires``
----------------------------

You can (and should) put ``setuphelpers`` in the ``setup_requires``
argument of your setup.py. But you also need to be careful to avoid
dependency problems during build. To accomplish this, you can use this
pattern (for each/any of the used functions):

.. code:: python

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

Now ``python setup.py install`` should pull in ``setuphelpers`` if it's
missing, and re-exec itself to fill in the arguments as expected. You
need to manually avoid both the ``ImportError`` and the ``NameError``
though, so mock callables need to be created in the case of missing
``setuphelpers``.

Copyright and License
=====================

setuphelpers was written by Adam Talsma

Copyright (c) 2016 CCP hf.

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be included
in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

.. |Build Status| image:: https://travis-ci.org/ccpgames/setuphelpers.svg?branch=master
   :target: https://travis-ci.org/ccpgames/setuphelpers
.. |Coverage Status| image:: https://coveralls.io/repos/ccpgames/setuphelpers/badge.svg?branch=master
   :target: https://coveralls.io/r/ccpgames/setuphelpers?branch=master
.. |Version| image:: https://img.shields.io/pypi/v/setuphelpers.svg
   :target: https://pypi.python.org/pypi/setuphelpers/
.. |Download format| image:: https://img.shields.io/badge/format-wheel-green.svg?
   :target: https://pypi.python.org/pypi/setuphelpers/
.. |Downloads this month| image:: https://img.shields.io/pypi/dm/setuphelpers.svg
   :target: https://pypi.python.org/pypi/setuphelpers/
.. |Development Status| image:: https://img.shields.io/badge/status-pre--alpha-red.svg
   :target: https://pypi.python.org/pypi/setuphelpers/
.. |License| image:: https://img.shields.io/github/license/ccpgames/setuphelpers.svg
   :target: https://pypi.python.org/pypi/setuphelpers/
