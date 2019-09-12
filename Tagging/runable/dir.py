import os
import sys


print(os.getcwd())

print(os.path.dirname(os.path.realpath(__file__)))

print(os.path.dirname(sys.modules['__main__'].__file__))