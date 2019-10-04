import unittest
import os
import sys


def main() -> unittest.TestSuite:
    suite = unittest.TestSuite()

    test_modules = []
    tests_dir = os.listdir(os.path.dirname(os.path.abspath(__file__)))

    for file in tests_dir:
        if file.startswith('test') and file.endswith('.py'):
            print("found: " + file)
            test_modules.append(file.rstrip('.py'))

    for test_module in map(__import__, test_modules):
        suite.addTest(unittest.defaultTestLoader.loadTestsFromModule(test_module))

    os.chdir(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), os.pardir))
    return suite


if __name__ == '__main__':
    sys.path.append('.')
    runner = unittest.TextTestRunner()
    runner.run(main())
