"""Tests for setuphelpers."""


import mock

import setuphelpers


def test_command_class__nose():
    with mock.patch.object(setuphelpers, "nose_command") as patchednose:
        setuphelpers.test_command(nose=True, foo="bar")
    assert patchednose.called_once_with(foo="bar")
