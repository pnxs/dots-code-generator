#!/usr/bin/env python3

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name="dots-cg-pnxs",
    version="0.0.1",
    author="Thomas Schaetzlein",
    author_email="pypi@thomas.pnxs.de",
    description="DOTS code generator",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pnxs/dots-code-generator",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GPL-3.0 License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
