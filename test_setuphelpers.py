"""Tests for setuphelpers."""


import io
import os
import mock
import tempfile

import setuphelpers


def test_command_class__nose():
    with mock.patch.object(setuphelpers, "nose_command") as patchednose:
        setuphelpers.test_command(nose=True, foo="bar")
    assert patchednose.called_once_with(foo="bar")


def test_command_class__unittest():
    with mock.patch.object(setuphelpers, "unittest_command") as patchedunit:
        setuphelpers.test_command(unittest=True, foo="bar")
    assert patchedunit.called_once_with(foo="bar")


def test_command_class__pytest():
    with mock.patch.object(setuphelpers, "pytest_command") as patchedpytest:
        setuphelpers.test_command(foo="bar")
    assert patchedpytest.called_once_with(foo="bar")


def test_long_description(capsys):
    os.chdir(tempfile.gettempdir())
    assert setuphelpers.long_description() == __doc__
    out, err = capsys.readouterr()
    assert err == ""
    assert out == "warning: missing readme, falling back to module docstring\n"


def test_long_description__readme():
    os.chdir(tempfile.gettempdir())
    with io.open("README.md", "w", encoding="utf-8") as openreadme:
        openreadme.write("words, things")
    assert setuphelpers.long_description() == "words, things"
    os.unlink("README.md")


def test_find_version():
    with tempfile.TemporaryDirectory() as tmpdir:
        thing_py = os.path.join(tmpdir, "thing.py")
        with io.open(thing_py, "w", encoding="utf-8") as openthing:
            openthing.write("__version__ = '0.1.2'")
        assert setuphelpers.find_version(thing_py) == "0.1.2"


def test_find_version__not_found():
    with tempfile.TemporaryDirectory() as tmpdir:
        thing_py = os.path.join(tmpdir, "thing.py")
        with io.open(thing_py, "w", encoding="utf-8") as openthing:
            openthing.write("version = '0.1.2'")
        assert setuphelpers.find_version(thing_py) == "0.0.0"


def test_pytest_command_class():
    pytest_cls = setuphelpers.pytest_command()
    self = mock.MagicMock()
    with mock.patch.object(setuphelpers.TestCommand, "finalize_options"):
        pytest_cls.finalize_options(self)
    assert self.test_suite is True
    assert self.test_args == ["-v", "-x", "-rx"]


def test_pytest_command_class__all_options():
    py_cls = setuphelpers.pytest_command(pdb=True, cover="foo", test_dir="bar")
    self = mock.MagicMock()
    with mock.patch.object(setuphelpers.TestCommand, "finalize_options"):
        py_cls.finalize_options(self)
    assert self.test_suite is True
    assert self.test_args == ["-v", "-x", "--pdb", "-rx", "--cov", "foo",
                              "--cov-report", "term-missing", "bar"]


def test_nose_command_class():
    nose_cls = setuphelpers.nose_command()
    self = mock.MagicMock()
    with mock.patch.object(setuphelpers.TestCommand, "finalize_options"):
        nose_cls.finalize_options(self)
    assert self.test_suite is True
    assert self.test_args == ["-v", "-d"]


def test_nose_command_class__all_options():
    nose_cls = setuphelpers.nose_command(cover="foo")
    self = mock.MagicMock()
    with mock.patch.object(setuphelpers.TestCommand, "finalize_options"):
        nose_cls.finalize_options(self)
    assert self.test_suite is True
    assert self.test_args == ["-v", "-d", "--with-coverage", "--cov-report",
                              "term-missing", "--cov", "foo"]


def test_unittest_command_class():
    unittest_cls = setuphelpers.unittest_command()
    self = mock.MagicMock()
    with mock.patch.object(setuphelpers.TestCommand, "finalize_options"):
        unittest_cls.finalize_options(self)
    assert self.test_args == []
    assert self.test_suite is True
