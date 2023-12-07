import unittest


def load_tests(loader, tests, pattern):
    suite = loader.discover('core/tests', pattern='test_*.py')
    return suite


if __name__ == '__main__':
    unittest.main()
