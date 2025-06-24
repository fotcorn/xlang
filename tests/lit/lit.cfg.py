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

# hook up FileCheck
filecheck_bin = shutil.which("FileCheck")
if not filecheck_bin:
    for i in range(18, 11, -1):
        filecheck_bin = shutil.which(f"FileCheck-{i}")
        if filecheck_bin:
            break
if not filecheck_bin:
    print("WARNING: FileCheck binary not found in PATH. Substituting with a command to save output to /tmp/fc_output_*.txt and print to stdout.")
    # Construct a command that uses the test file name (%s) to create a unique output file.
    # lit will replace %s with the current test file path. We need just the basename for the output file.
    # Using tee to both save to file and pass to stdout (which lit captures).
    # The actual FileCheck options will be passed to this command string by lit,
    # so the receiving command ('cat' in this case, after tee) should ideally ignore them.
    # Using "cat -" to ensure it reads from stdin piped from tee.
    filecheck_replacement = (
        "sh -c 'mkdir -p /tmp/xlang_lit_outputs && "
        "OUTPUT_FILE=/tmp/xlang_lit_outputs/$(basename %s .xl).actual.txt && "
        "echo \"--- Output for %s --- \" > $OUTPUT_FILE && "
        "tee -a $OUTPUT_FILE | cat -'"
    )
    config.substitutions.append(("%filecheck", filecheck_replacement))
else:
    config.substitutions.append(("%filecheck", f"{filecheck_bin}"))
