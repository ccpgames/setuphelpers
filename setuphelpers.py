"""Setuptools helper functions."""


import io
import os
import re
import inspect
from codecs import decode
from subprocess import check_output
from subprocess import CalledProcessError
from pkg_resources import parse_version
from setuptools.command.test import test as TestCommand


def long_description():
    """Returns the contents of a README markdown or ReST file.

    If no README can be found, returns the calling module's docstring.
    """

    extensions = (".md", ".rst")
    for file_ in os.listdir(os.curdir):
        file_name, file_ext = os.path.splitext(file_)
        if file_name.lower() == "readme" and file_ext.lower() in extensions:
            return _read_file(file_)
    else:
        print("warning: missing readme, falling back to module docstring")
        called_from = inspect.getmodule(inspect.stack()[1][0])
        return called_from.__doc__


def find_version(filename):
    """Uses re to pull out the assigned value to __version__ in filename."""

    contents = _read_file(filename)
    match = re.search(r'^__version__ = [\'"]([^\'"]*)[\'"]', contents, re.M)
    if match:
        return match.group(1)
    return "0.0.0"


def test_command(pytest=True, nose=False, unittest=False, **kwargs):
    """Builds a dictionary suitable for setup's cmdclass.

    Args:
        pytest: boolean to use pytest (default)
        nose: boolean to use nose
        unittest: boolean to use unittest

    KWArgs:
        any other settings you want to change in the specified runner

    Returns:
        dict of {"test": TestCommandClass}
    """

    if nose:
        test_class = nose_command(**kwargs)
    elif unittest:
        test_class = unittest_command(**kwargs)
    else:
        test_class = pytest_command(**kwargs)

    return {"test": test_class}


def pytest_command(verbose=True, exit_first=True, pdb=False, extra_fails=True,
                   cover=None, test_dir=None):
    """Returns the PyTest TestCommand runner.

    You can use this directly if you want, or pass any of these kwargs to
    test_command instead.

    KWArgs:
        verbose: print verbose test output
        exit_first: exit on the first test failure
        pdb: drop to a pdb session on test failure
        extra_fails: print extra/detailed information on test failure
        cover: string module to display a coverage report for
        test_dir: string path to tests, if required for discovery

    Returns:
        CommandClass object
    """

    test_args = []
    if verbose:
        test_args.append("-v")
    if exit_first:
        test_args.append("-x")
    if pdb:
        test_args.append("--pdb")
    if extra_fails:
        test_args.append("-rx")
    if cover:
        test_args.extend(["--cov", cover, "--cov-report", "term-missing"])
    if test_dir:
        test_args.append(test_dir)

    class PyTest(TestCommand):
        """TestCommand subclass to enable setup.py test."""

        def finalize_options(self):
            """Fill out test_args."""

            TestCommand.finalize_options(self)
            self.test_suite = True
            self.test_args = test_args

        def run_tests(self):  # pragma: no cover
            """Pytest discovery and test execution."""

            import pytest
            raise SystemExit(pytest.main(self.test_args))

    return PyTest


def nose_command(verbose=True, detailed=True, cover=None):
    """Returns the NoseTest TestCommand runner.

    You can use this directly if you want, or pass any of these kwargs to
    test_command instead, while also passing nose=True.

    KWArgs:
        verbose: print verbose test output
        detailed: print extra/detailed information on test failure
        cover: string module to display a coverage report for

    Returns:
        CommandClass object
    """

    test_args = []
    if verbose:
        test_args.append("-v")
    if detailed:
        test_args.append("-d")
    if cover:
        test_args.extend(["--with-coverage", "--cov-report",
                          "term-missing", "--cov", cover])

    class NoseTest(TestCommand):
        """TestCommand subclass to enable setup.py test."""

        def finalize_options(self):
            """Fill out test_args."""

            TestCommand.finalize_options(self)
            self.test_suite = True
            self.test_args = test_args

        def run_tests(self):  # pragma: no cover
            """Nose test discovery and execution."""

            import nose
            raise SystemExit(nose.main(argv=self.test_args))

    return NoseTest


def unittest_command(test_dir="tests"):
    """Returns the UnitTest TestCommand runner.

    You can use this directly if you want, or pass any of these kwargs to
    test_command instead, while also passing unittest=True.

    KWArgs:
        test_dir: string path to tests, if required for discovery

    Returns:
        CommandClass object
    """

    class UnitTest(TestCommand):
        """TestCommand subclass to enable setup.py test."""

        def finalize_options(self):
            """Fill out test_args."""

            TestCommand.finalize_options(self)
            self.test_suite = True
            self.test_args = []

        def run_tests(self):  # pragma: no cover
            """Unittest discovery and test execution."""

            import unittest
            test_suite = unittest.defaultTestLoader.discover(
                os.path.abspath(test_dir)
            )
            raise SystemExit(unittest.TextTestRunner().run(test_suite))

    return UnitTest


def git_version():
    """Returns a string of the version according to git tags.

    Use PEP440 compatable git tags. Tag sort order is PEP440, not time.

    If the latest commit is tagged, this will return that tag. Otherwise,
    this will add 1 to the latest tag's most minor version number, and
    append .devN, where N is the number of commits since the latest tag.

    For repos without any tags, the version will be 0.0.1.devN where
    N is the total amount of commits.

    Keep in mind that .devN releases are considered OLDER than releases
    without a .devN suffix.

    If we are building a package from a branch other than master,
    +branch name is appended as the local version identifier.

    If we are running on travis.ci, use the environment variables available.
    """

    try:
        branch = os.environ.get("TRAVIS_BRANCH", _get_branch())
    except (OSError, IOError, CalledProcessError):
        print("warning: could not determine active git branch")
        branch = "master"

    git_tag = os.environ.get("TRAVIS_TAG")
    if git_tag:
        is_dev = False
        dev_release = 0
        branch = "master"
    else:
        if _has_tags():
            git_tag = _lastest_tag()
            dev_release = _commits_since(_tag_ref(git_tag))
            is_dev = dev_release > 0
            if is_dev:
                git_tag = _plus_one_minor(git_tag)
        else:
            print("warning: git tag version requested but no tags found")
            git_tag = "0.0.1"
            is_dev = True
            try:
                dev_release = _commits_since()
            except (OSError, IOError, CalledProcessError):
                print("warning: no commits found, assuming first dev release")
                dev_release = 1

    return "{}{}{}".format(
        git_tag,
        ".dev{}".format(dev_release) if is_dev else "",
        "" if branch == "master" else "+{}".format(branch),
    )


def _has_tags():
    """Returns a boolean of if any git tags exist."""

    try:
        return len(check_output(["git", "tag"]).splitlines()) > 0
    except:
        return False


def _lastest_tag():
    """Gets the latest git tag according to PEP440."""

    latest_tag = parse_version("0.0.0")
    for tag in check_output(["git", "tag"]).splitlines():
        tag_version = parse_version(_decoded(tag))
        if tag_version > latest_tag:
            latest_tag = tag_version
    return latest_tag.public


def _tag_ref(git_tag):
    """Returns the ref for a tag."""

    return _decoded(check_output(["git", "show-ref", git_tag])).split(" ")[0]


def _read_file(file_):
    """Reads a file, returns the stripped contents."""

    with io.open(file_, "r", encoding="utf-8") as openfile:
        return openfile.read().strip()


def _commits_since(ref=None):
    """Returns the integer number of commits since ref (or None for all)."""

    cmd = ["git", "rev-list", "--all", "--no-merges", "--count"]
    if ref:
        cmd.append("{}..HEAD".format(ref))
    return int(check_output(cmd))


def _plus_one_minor(version):
    """Adds 1 to the most minor version number."""

    old_version = parse_version(version)
    new_version = parse_version(".".join(
        str(v) for v in list(old_version._version.release[:-1]) +
        [old_version._version.release[-1] + 1]
    ))
    return new_version.public


def _get_branch():
    """Returns the string branch name HEAD is pointing at."""

    branch = _decoded(check_output(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"]
    )).strip()
    if branch == "HEAD":
        print("warning: HEAD is detatched? assuming master branch")
        branch = "master"
    return branch


def _decoded(string):
    """Decodes byte strings."""

    if isinstance(string, bytes):
        string = decode(string, "utf-8")
    return string
