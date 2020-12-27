import logging
from .top import Top
from ..boards import stemlab125_14


def build():
    logging.basicConfig()
    logging.root.setLevel(logging.DEBUG)
    stemlab125_14.build(Top)


if __name__ == "__main__":
    build()
