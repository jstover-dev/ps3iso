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
            parse_args(['-i', self.SFO_FILE, '-r'])

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

        #main(['-i', self.SFO_FILE])
