#!/usr/bin/env python
"""
Builds packages so that each package can be imported (and allow relative imports)

"""
import dockerprettyps
import setuptools

setuptools.setup(
    name="Docker-Pretty-PS",
    version="v%s" % dockerprettyps.__version__,
    author="politeauthority",
    url="https://github.com/politeauthority/docker-pretty-ps",
    download_url="https://github.com/politeauthority/docker-pretty-ps/archive/v0.0.1.tar.gz",
    packages=setuptools.find_packages(),
    scripts=['dockerprettyps/bin/docker-pretty-ps'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
