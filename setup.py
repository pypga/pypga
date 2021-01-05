from setuptools import setup, find_packages


with open('requirements.txt') as f:
    requirements = f.readlines()


setup(
    name='pypga',
    version='1.0.0',
    packages=find_packages(),
    install_requires=(
        "migen",
        "misoc",
        "migen-axi",
        "pydantic>=1.5.1",
        "paramiko>=2.7.2",
    ),
)
