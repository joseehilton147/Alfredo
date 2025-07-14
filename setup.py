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
    requirements = f.read().splitlines()

setup(
    name='alfredo-ai',
    version='1.0.0',
    author='Josee Hilton',
    author_email='josee@example.com',
    description='AI-powered video transcription and summarization tool',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/joseehilton147/alfredo-ai',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Multimedia :: Video',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    python_requires='>=3.8',
    install_requires=requirements,
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-cov>=4.0.0',
            'black>=22.0.0',
            'flake8>=5.0.0',
            'mypy>=1.0.0',
            'pre-commit>=2.20.0',
            'bandit>=1.7.0',
        ],
        'docs': [
            'sphinx>=5.0.0',
            'sphinx-rtd-theme>=1.0.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'alfredo=alfredo_ai.cli:main',
            'alfredo-ai=alfredo_ai.cli:main',
        ],
    },
    include_package_data=True,
    package_data={
        'alfredo_ai': ['config/*.yaml', 'templates/*.txt'],
    },
    zip_safe=False,
)
