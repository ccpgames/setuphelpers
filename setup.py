"""Helpers for setuptools. Dogfood our own functions here."""


from setuptools import setup
from importlib import import_module

setuphelpers = import_module("setuphelpers")


setup(
    name="setuphelpers",
    version=setuphelpers.git_version(),
    description="Setuptools helper functions",
    author="Adam Talsma",
    author_email="se-adam.talsma@ccpgames.com",
    url="https://github.com/ccpgames/setuphelpers/",
    download_url="https://github.com/ccpgames/setuphelpers/",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Operating System :: POSIX :: Linux",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development",
        "Topic :: System :: Archiving :: Packaging",
        "Topic :: Utilities",
    ],
    py_modules=["setuphelpers"],
    long_description=setuphelpers.long_description(),
    cmdclass=setuphelpers.test_command(cover="setuphelpers", pdb=True),
    tests_require=["pytest", "pytest-cov", "mock"],
)
