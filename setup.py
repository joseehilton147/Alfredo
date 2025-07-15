#!/usr/bin/env python3
"""Setup script for Alfredo AI."""

from setuptools import setup, find_packages
import os

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Read requirements
with open('requirements.txt') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name='alfredo-ai',
    version='1.0.0',
    author='Jose Hilton',
    author_email='joseehilton147@gmail.com',
    description='AI-powered video transcription and analysis tool',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/joseehilton147/alfredo-ai',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Multimedia :: Video',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
    ],
    python_requires='>=3.8',
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'alfredo=src.main:main',
        ],
    },
    keywords='ai video transcription whisper',
    project_urls={
        'Bug Reports': 'https://github.com/joseehilton147/alfredo-ai/issues',
        'Source': 'https://github.com/joseehilton147/alfredo-ai',
    },
)
