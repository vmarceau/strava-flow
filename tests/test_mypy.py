import unittest
import mypy.api


class TypeChecker(unittest.TestCase):
    def test_check_type_for_all_modules(self) -> None:
        stdout, stderr, exit_code = mypy.api.run(['--strict', 'strava_flow'])
        self.assertEqual(exit_code, 0, f'mypy validation failed\r\nType errors:\r\n{stdout}\r\nErrors:\r\n{stderr}')
