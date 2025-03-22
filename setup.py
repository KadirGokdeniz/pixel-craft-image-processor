#!/usr/bin/env python3
"""
Setup script for PixelCraft.

This script provides the installation and packaging functionality for the
PixelCraft application.
"""

import os
from setuptools import setup, find_packages

# Get the long description from the README file
with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

# Get the version from version.py
version = {}
with open("src/version.py", encoding="utf-8") as f:
    exec(f.read(), version)

# Read requirements
with open("requirements.txt", encoding="utf-8") as f:
    requirements = f.read().splitlines()

setup(
    name="pixelcraft",
    version=version.get("__version__", "1.0.0"),
    description="Professional image processing application with customizable filters and similarity analysis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/KadirGokdeniz/pixel-craft-image-processor",
    author="Kadir Gökdeniz",
    author_email="kadirqokdeniz@hotmail.com",
    license="MIT",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Image Processing",
        "Topic :: Multimedia :: Graphics :: Editors",
        "Topic :: Utilities",
        "Operating System :: OS Independent",
    ],
    keywords="image processing, filters, computer vision, similarity analysis, GUI",
    packages=find_packages(include=["src", "src.*"]),
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "pixelcraft=src.main:main",
        ],
        "gui_scripts": [
            "pixelcraft-gui=src.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "pixelcraft": [
            "resources/images/*.jpg",
            "resources/images/*.png",
            "resources/icons/*.png",
            "resources/icons/*.ico",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/KadirGokdeniz/pixel-craft-image-processor/issues",
        "Source": "https://github.com/KadirGokdeniz/pixel-craft-image-processor",
    },
)