"""Run the local laboratory even when invoked from another directory."""
import os
from pathlib import Path
import runpy
import sys


if __name__ == '__main__':
    if sys.version_info < (3, 10):
        raise SystemExit('VGC requires Python 3.10 or newer.')
    root = Path(__file__).resolve().parent
    os.chdir(root)
    sys.path.insert(0, str(root))
    runpy.run_module('vgc_sd.server', run_name='__main__')
