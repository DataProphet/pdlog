#! /usr/bin/env python

from setuptools import find_packages, setup

setup(
    name="pdlog",
    version="0.0.1",
    description="Logging for pandas dataframes",
    author="Wasim Lorgat",
    author_email="wasim@dataprophet.com",
    packages=find_packages(),
    install_requires=[
        "pandas",
        "typing_extensions"
    ],
)
