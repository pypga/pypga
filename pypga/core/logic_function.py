logic_registry = []


def logic(function):
    """A descriptor to tag a function as programmable logic, contianing migen commands."""
    logic_registry.append(function)
    return function


def is_logic(function):
    """Returns True if the given function was tagged using the ``@logic`` descriptor."""
    return function in logic_registry
