from .builder import Builder


def build(Top):
    builder = Builder(module_class=Top)
    builder.build()
