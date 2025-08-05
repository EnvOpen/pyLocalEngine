#!/usr/bin/env python3
"""
Setup script for pyLocalEngine - Python implementation of the LocalEngine framework.
"""

from setuptools import setup, find_packages
import os

# Read the README file for the long description
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    with open(readme_path, 'r', encoding='utf-8') as f:
        return f.read()

setup(
    name="pyLocalEngine",
    version="0.1.0",
    author="Argo Nickerson",
    author_email="code@envopen.org",
    description="Python implementation of the LocalEngine localization framework",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/EnvOpen/pyLocalEngine",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Lesser General Public License v2 (LGPLv2)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Internationalization",
        "Topic :: Software Development :: Localization",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pyyaml>=6.0",
        "requests>=2.25.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "isort>=5.10.0",
            "mypy>=1.0.0",
            "flake8>=6.0.0",
            "types-requests>=2.25.0",
            "types-PyYAML>=6.0.0",
        ]
    },
    keywords="localization internationalization i18n l10n locale translation",
    project_urls={
        "Bug Reports": "https://github.com/EnvOpen/pyLocalEngine/issues",
        "Source": "https://github.com/EnvOpen/pyLocalEngine",
        "Documentation": "https://github.com/EnvOpen/pyLocalEngine/blob/main/USER.md",
    },
)
