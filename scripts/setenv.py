#!/usr/bin/env python3

import platform
import sys
import os
import getpass
import datetime

AZIONA_PATH = os.path.join(os.getenv("HOME"), ".aziona")

if platform.system() == "Darwin":
  AZIONA_WORKSPACE_PATH = "/Users/" + getpass.getuser() + "/Documents/projects/azionaventures"
if platform.system() == "Linux":
  AZIONA_WORKSPACE_PATH = "/opt/project/azionaventures"

ENV = {
    "AZIONA_WS_VERSION": "1.0",
    "AZIONA_ACTIVE_PATH": "/tmp/.aziona_active",
    "AZIONA_PATH": AZIONA_PATH,
    "AZIONA_ENV_PATH": os.path.join(AZIONA_PATH, ".env"),
    "AZIONA_ACTIVE_PERSISTENT_PATH": os.path.join(AZIONA_PATH, ".aziona_active_perisistent"),
    "AZIONA_BIN_PATH": os.path.join(AZIONA_PATH, "bin"),
    "AZIONA_TERRAFORM_MODULES_PATH": os.path.join(AZIONA_PATH, "terraform-modules"),
    "AZIONA_TENANT_PATH": os.path.join(AZIONA_PATH, "tenant"),
    "AZIONA_WORKSPACE_PATH": AZIONA_WORKSPACE_PATH,
    "AZIONA_WORKSPACE_INFRASTRUCTURE": os.path.join(AZIONA_WORKSPACE_PATH, "/infrastructure"),
    "AZIONA_WORKSPACE_AZIONACLI": os.path.join(AZIONA_WORKSPACE_PATH, "/aziona-cli")
}

RC = """
# AZIONA CONFIG (configured in %s)
source ~/.aziona/.env
source ${AZIONA_ACTIVE_PERSISTENT_PATH:-}
export PATH=$PATH:$AZIONA_BIN_PATH
# AZIONA CONFIG END
""" % datetime.datetime.now()

def _configurations():
    try:
        os.makedirs(f"{ENV['AZIONA_WORKSPACE_PATH']}", exist_ok=True)
    except Exception:
        print(f"{ENV['AZIONA_WORKSPACE_PATH']} skip creation.")
        return 1

    os.makedirs(f"{ENV['AZIONA_PATH']}", exist_ok=True)
    os.makedirs(f"{ENV['AZIONA_TENANT_PATH']}", exist_ok=True)
    os.makedirs(f"{ENV['AZIONA_BIN_PATH']}", exist_ok=True)
    os.makedirs(f"{ENV['AZIONA_TERRAFORM_MODULES_PATH']}", exist_ok=True)

    if os.path.isfile(ENV["AZIONA_ENV_PATH"]) is True:
        os.rename(ENV["AZIONA_ENV_PATH"], ENV["AZIONA_ENV_PATH"] + ".old")

    with open(ENV["AZIONA_ENV_PATH"], "w") as f:
        for key, value in ENV.items():
            f.write(f"export {key}={value}\n")

    with open(ENV["AZIONA_ACTIVE_PERSISTENT_PATH"], "w") as f:
        f.write("")

    confirm = True if input("Add source in .bashrc or/and .zshrc [y,yes or n,no]: ").lower() in ["y","yes"] else False

    if confirm is False:
        print("Add in shell configurtion file: \n" + RC + "\n")
        import time
        time.sleep(1.0)
        return 0

    bashrc_path = os.getenv("HOME") + "/.bashrc"
    if os.path.isfile(bashrc_path):
        with open(bashrc_path, "r") as f:
            if "AZIONA CONFIG" not in f.read():
                with open(bashrc_path, "a") as f:
                    f.write(RC)

    zshrc_path = os.getenv("HOME") + "/.zshrc"
    if os.path.isfile(zshrc_path):
        with open(zshrc_path, "r") as f:
            if "AZIONA CONFIG" not in f.read():
                with open(zshrc_path, "a") as f:
                    f.write(RC)

def main():
    try:
        _configurations()
    except KeyboardInterrupt as e:
        pass

if __name__ == "__main__":
    sys.exit(main())