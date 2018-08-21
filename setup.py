from setuptools import setup
from os import path
from io import open

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='displaycontrol',
    version='0.0.3.dev1',
    packages=['displaycontrol'],
    license='Creative Commons Attribution-Noncommercial-Share Alike license',
    description='Package to control displays and projectors via serial and ethernet connection.',
    long_description=long_description,
    url='https://github.com/TopRedMedia/displaycontrol',
    author='Mirko Haaser',
    author_email='mirko@topred.media',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: System :: Hardware',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
    ]
)
