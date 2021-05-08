
from setuptools import setup, find_packages

setup(name='Shopify code challenege image repo',
    version='1.0',
    description='code challenge for deverloper intern Fall 2021',
    author='Jeffer Peng',
    packages=find_packages(exclude="tests"),
    install_requires=[
        'pytest', 
        'pytest-mock',
        'aiohttp==3.7.4.post0',
        'aiofiles==0.6.0',
        'Flask==1.1.1',
        'Flask-Cors==3.0.8',
        'requests==2.22.0',
        'chardet==3.0.4',
        'pytest-mock==3.6.1',
    ],
    python_requires='>=3.7',
)