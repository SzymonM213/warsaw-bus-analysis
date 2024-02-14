from setuptools import setup, find_packages

setup(
    name='fetch',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'pandas',
        'requests',
        'tqdm',
        'geopy'
    ],
    description='A package for fetching data from the Warsaw API.'
)