#!/usr/bin/env python
"""
Builds packages so that each package can be imported (and allow relative imports)

"""

import setuptools

setuptools.setup(
    name="Docker-Pretty-PS",
    version="0.0.1",
    author="politeauthority",
    url="https://github.com/politeauthority/docker-pretty-ps",
    packages=setuptools.find_packages(),
    scripts=['dockerprettyps/bin/docker-pretty-ps'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
