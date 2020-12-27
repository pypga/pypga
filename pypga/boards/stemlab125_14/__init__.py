from .builder import StemlabBuilder


def build(Top):
    builder = StemlabBuilder(Top=Top)
    builder.build()
