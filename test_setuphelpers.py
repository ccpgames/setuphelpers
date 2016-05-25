"""Tests for setuphelpers."""


import mock

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
