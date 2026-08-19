import configparser
import logging
import sys
import unittest
from pathlib import Path

logger = logging.getLogger(__name__)


class spinlab_configparse_tester(unittest.TestCase):
    def test_escape_split(self):
        p = Path(__file__).parent.joinpath("spinlab")
        sys.path.insert(0, str(p))
        from spinlab import config as slconfig

        cfg = configparser.ConfigParser(
            converters={
                "list": lambda x: list(x.strip("[").strip("]").split(",")),
                "args_kwargs": slconfig.config._kwarg_converter,
            }
        )

        string1 = "Contact Time t$_c$ [s]"

        cfg_file = str(Path(__file__).parent.joinpath("data_testconfig.cfg"))
        cfg.read(cfg_file)

        args2, kwargs2 = cfg.getargs_kwargs("UNITTEST_EXAMPLE", "test1")
        logger.info("{0}\n{1}".format(args2, kwargs2))
        self.assertEqual(len(args2), 1)
        self.assertEqual(len(kwargs2), 2)
        self.assertEqual(kwargs2["ghi"], "3")
        self.assertEqual(args2[0], "def=2")

        args1, kwargs1 = cfg.getargs_kwargs("UNITTEST_EXAMPLE", "test0")
        logger.info("{0}\n{1}".format(args1, kwargs1))
        self.assertEqual(len(args1), 1)
        self.assertEqual(len(kwargs1), 0)
        self.assertEqual(args1[0], string1)


if __name__ == "__main__":
    unittest.main()
