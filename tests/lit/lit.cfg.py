import os
import shutil
import subprocess

import lit.formats
from lit import TestingConfig

config: TestingConfig

config.name = "xlang"

config.test_format = lit.formats.ShTest(True)

config.suffixes = [".xl"]

lit_cfg_dir = os.path.dirname(__file__)
main_py_path = os.path.abspath(os.path.join(lit_cfg_dir, "../../main.py"))

config.substitutions.append(("%run", f"python {main_py_path}"))

filecheck_bin = shutil.which("filecheck")
config.substitutions.append(("%filecheck", f"{filecheck_bin}"))
