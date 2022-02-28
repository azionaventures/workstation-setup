#!/usr/bin/env python3

import sys
import os
import pathlib

def _scripts():
    import shutil

    if os.getenv("AZIONA_BIN_PATH") is None:
        print("AZIONA_BIN_PATH not found in ENV vars")
        return 1

    source_dir = pathlib.Path(pathlib.Path(__file__).parent.resolve(), "..", "bin") 
    dest_dir = pathlib.Path(os.getenv("AZIONA_BIN_PATH"))
    
    for file_name in os.listdir(source_dir):
        source = pathlib.Path(source_dir, file_name)
        destination = pathlib.Path(dest_dir, file_name)
        if os.path.isfile(source):
            shutil.copy(source, destination)
            print(f"Copied {file_name} in {destination}")

def main():
    try:
        _scripts()
    except KeyboardInterrupt as e:
        pass

if __name__ == "__main__":
    sys.exit(main())