import runpy
import sys


if __name__ == "__main__":
    sys.path.append("src")
    module_name = "folder_sync"
    runpy.run_module(module_name, run_name="__main__")
