# Always prefer setuptools over distutils
from setuptools import setup, find_packages

# To use a consistent encoding
from codecs import open
from os import path

# The directory containing this file
HERE = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(HERE, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# This call to setup() does all the work
setup(
    name="cacao",
    version="0.0.4",
    description="Library for dynamic optimization/simulation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    project_urls={  # Optional
        'Documentation': "https://cacao.readthedocs.io/",
        'Source': 'https://github.com/euanrussano/cacao',
    },
    #    url="https://cacao.readthedocs.io/",
    author="Euan Russano",
    author_email="euanrussano@gmail.com",
    license="MIT",
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent"
    ],
    packages=["cacao"],
    include_package_data=True,
    install_requires=["numpy", "scipy"]
)
