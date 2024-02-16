from setuptools import setup, find_packages

setup(
    name='fetch',
    version='1.0',
    packages=find_packages(),
    install_requires=[
        'pandas',
        'requests',
        'tqdm',
        'geopy',
        'matplotlib',
        'folium'
    ],
    description='A package for fetching data from the Warsaw API.'
)