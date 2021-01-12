#!/usr/bin/env python

from genologics_mock import __version__ as version
from setuptools import setup, find_packages

try:
    with open("requirements.txt", "r") as f:
        install_requires = [x.strip() for x in f.readlines()]
except IOError:
    install_requires = []

with open("README.md", "r") as fh:
    long_description = fh.read()


setup(name='genologics_mock',
      version=version,
      description="Mock for the genologics package",
      long_description=long_description,
      long_description_content_type="text/markdown",
      author='Maya Brandi',
      author_email='maya.brandi@scilifelab.se',
      packages=find_packages(),
      url="https://github.com/Clinical-Genomics/genologics_mock",
      include_package_data=True,
      entry_points={"console_scripts": ["gmock=genologics_mock.cli:cli"], },
      classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        ],
      python_requires='>=3.6',
      )
