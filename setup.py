from setuptools import setup, find_packages

setup(
    name='terminus',
    version='0.0.1',
    description='Where you put the tools to build your foundation',
    author='Spencer Everett',
    author_email='spencerweverett@gmail.com',
    url='https://github.com/sweverett/terminus',
    packages=find_packages(),
    install_requires=['numpy', 'astropy', 'pyyaml'],
)
