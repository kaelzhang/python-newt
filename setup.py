import os
from pathlib import Path
from setuptools import setup

from newt import __version__

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(Path(__file__).parent / 'docs' / 'README.md').read()

def read_requirements(filename):
    with open(filename) as f:
        return f.read().splitlines()

settings = dict(
    name = 'newt',
    packages = ['newt'],
    version = __version__,
    author = 'kaelzhang',
    author_email = '',
    description = ('Thread-safe, mixed sync-async queue for Python'),
    license = 'MIT',
    keywords = 'newt',
    url = 'https://github.com/kaelzhang/python-newt',
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    python_requires='>=3.7',
    # install_requires=read_requirements('requirements.txt'),
    tests_require=read_requirements('test-requirements.txt'),
    classifiers=[
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
    ]
)


if __name__ == '__main__':
    setup(**settings)
