#!/usr/bin/env python
"""
Builds packages so that each package can be imported (and allow relative imports)

"""
import dockerprettyps
import setuptools

setuptools.setup(
    name="docker-pretty-ps",
    version=dockerprettyps.__version__,
    author="politeauthority",
    author_email="fullteronalix0@gmail.com",
    url="https://github.com/politeauthority/docker-pretty-ps",
    download_url="https://github.com/politeauthority/docker-pretty-ps/archive/v0.0.1-alpha.zip",
    packages=setuptools.find_packages(),
    entry_points={
        "console_scripts": [
            "docker-pretty-ps = dockerprettyps:run_cli",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
