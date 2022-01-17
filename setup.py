#!/usr/bin/env python3

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name="dots-code-generator",
    version="0.1.0",
    author="Thomas Schaetzlein",
    author_email="pypi@thomas.pnxs.de",
    description="DOTS code generator",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pnxs/dots-code-generator",
    packages=setuptools.find_packages(),
    install_requires=['jinja2'],
    scripts=[
        'bin/dcg.py'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)
