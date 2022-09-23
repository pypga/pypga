from setuptools import setup, find_packages


setup(
    name='pypga',
    version='1.0.0',
    packages=find_packages(),
    install_requires=(
        "migen@git+https://github.com/pypga/migen@master",
        "misoc@git+https://github.com/pypga/misoc@master",
        "migen-axi@git+https://github.com/pypga/migen-axi@master",
        "pydantic>=1.5.1",
        "paramiko>=2.7.2",
        "scp>=0.14.1",
        "numpy>=1.21.4",
    ),
)
