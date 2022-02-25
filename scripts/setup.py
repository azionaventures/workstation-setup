#!/usr/bin/env python3

import platform
import sys
import argparse
import os
import subprocess
import getpass
import datetime
from shutil import which

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

def argsinstance():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--only-scripts",
        action="store_true",
        default=False,
        help="Update only scripts",
    )
    parser.add_argument(
        "--only-depends",
        action="store_true",
        default=False,
        help="Update only dependencies",
    )
    parser.add_argument(
        "-y", "--yes",
        action="store_true",
        default=False,
        help="Accept request intput",
    )
    return parser


def scripts():
    import shutil

    source_dir = "../bin/"
    dest_dir = ENV["AZIONA_BIN_PATH"] + "/"
    
    for file_name in os.listdir(source_dir):
        source = source_dir + file_name
        destination = dest_dir + file_name
        if os.path.isfile(source):
            shutil.copy(source, destination)
            print('copied', file_name)

def configurations(args):
    try:
        os.makedirs(f"{ENV['AZIONA_WORKSPACE_PATH']}", exist_ok=True)
    except Exception:
        print(f"{ENV['AZIONA_WORKSPACE_PATH']} skip creation.")

    os.makedirs(f"{ENV['AZIONA_PATH']}", exist_ok=True)
    os.makedirs(f"{ENV['AZIONA_TENANT_PATH']}", exist_ok=True)
    os.makedirs(f"{ENV['AZIONA_BIN_PATH']}", exist_ok=True)
    os.makedirs(f"{ENV['AZIONA_TERRAFORM_MODULES_PATH']}", exist_ok=True)

    if os.path.isfile(ENV["AZIONA_ENV_PATH"]) is True:
        os.rename(ENV["AZIONA_ENV_PATH"], ENV["AZIONA_ENV_PATH"] + ".old")

    with open(ENV["AZIONA_ENV_PATH"], "w") as f:
        for key, value in ENV.items():
            f.write("export " + key + "=" + value + "\n")

    with open(ENV["AZIONA_ACTIVE_PERSISTENT_PATH"], "w") as f:
        f.write("")

    confirm = True if args.yes or input("Add source in .bashrc or .zshrc [y,yes or n,no]: ").lower() in ["y","yes"] else False

    if confirm is False:
        print("Add in shell configurtion file: \n" + RC + "\n")
        import time
        time.sleep(1.0)
        return

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

def dependencies():
    import platform

    if which("aziona") is None:
        subprocess.check_call("pip install aziona", shell=True)
    
    if platform.system() == "Darwin":
        if which("aws") is None:
            subprocess.check_call("brew install awscli", shell=True)
        install_dependencies_command = """cd /tmp && \
            curl -O "https://raw.githubusercontent.com/azionaventures/aziona-cli/main/bin/aziona-dependencies" && \
            chmod +x aziona-dependencies && \
            ./aziona-dependencies"""

    if platform.system() == "Linux":
        if which("aws") is None:
            subprocess.check_call("""
                curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && \
                unzip awscliv2.zip && \
                sudo ./aws/install --bin-dir /usr/local/bin --install-dir /usr/local/aws-cli --update && \
                aws --version && \
                rm -Rf ./aws && \
                rm awscliv2.zip""", shell=True)

        install_dependencies_command = """cd /tmp && \
            curl -O "https://raw.githubusercontent.com/azionaventures/aziona-cli/main/bin/aziona-dependencies" && \
            chmod +x aziona-dependencies && \
            sudo ./aziona-dependencies"""

    subprocess.check_call(install_dependencies_command, shell=True)

def main():
    try:
        args = argsinstance().parse_args()

        configurations(args)

        if args.only_scripts is False:
            dependencies()
            
        if args.only_depends is False:
            scripts()
    except KeyboardInterrupt as e:
        pass

if __name__ == "__main__":
    sys.exit(main())