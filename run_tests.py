import unittest
from tests import *

# Run tests in order
unittest.TestLoader.sortTestMethodsUsing = None

# Run tests
if __name__ == '__main__':
    unittest.main(verbosity=2, catchbreak=True)
