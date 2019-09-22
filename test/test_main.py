import os
import unittest


class TestSfoFile(unittest.TestCase):

    SFO_FILE = 'test/data/PARAM.SFO'

    def test_parse_args(self):
        from ps3iso.__main__ import parse_args, ArgumentParserError

        with self.assertRaises(ArgumentParserError):
            parse_args([])

        with self.assertRaises(ArgumentParserError):
            parse_args(['-r', '-f', '%T'])

        with self.assertRaises(ArgumentParserError):
            parse_args(['-i', self.SFO_FILE, '--rename'])

        args = parse_args(['-i', self.SFO_FILE])
        self.assertEqual(str(args.input), self.SFO_FILE)

        args = parse_args(['-i', self.SFO_FILE, '-f', '%T'])
        self.assertEqual(str(args.input), self.SFO_FILE)
        self.assertEqual(str(args.format), '%T')

    def test_main(self):
        from importlib.machinery import SourceFileLoader
        import ps3iso.__main__

        # noinspection PyTypeChecker
        with self.assertRaises(SystemExit):
            SourceFileLoader('__main__', ps3iso.__main__.__file__).load_module()

    def test_main_fn(self):
        from ps3iso.__main__ import main

        # noinspection PyTypeChecker
        with self.assertRaises(SystemExit):
            main(['-r'])

        # Run the rename_all path
        main(['-i', '.', '--rename', '-f', '""'])

        # Run the info path
        main(['-i', '.'])

        # Force isoinfo to not be found in PATH
        path = os.environ['PATH']
        del os.environ['PATH']
        try:
            main(['-i', '.'])
        except SystemExit:
            pass
        finally:
            os.environ['PATH'] = path
