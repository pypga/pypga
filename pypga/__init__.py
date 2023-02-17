"""
PYthon Programmable Gate Array
"""
import os
from . import boards, core, modules
from .core import interface

class config:
    user = os.getenv("REDPITAYA_USERNAME", "root")
    password = os.getenv("REDPITAYA_PASSWORD", "root")