#!/usr/bin/env python3

import platform
import sys
import argparse
import os
import subprocess
import getpass
import datetime
from shutil import which

ENV = {}

ENV["AZIONA_PATH"] = os.getenv("HOME") + "/.aziona"
ENV["AZIONA_ENV_PATH"] = ENV["AZIONA_PATH"] + "/.env"
ENV["AZIONA_ACTIVE_PATH"] = "/tmp/.aziona_active"
ENV["AZIONA_ACTIVE_PERSISTENT_PATH"] = ENV["AZIONA_PATH"] + "/.aziona_active_perisistent"
ENV["AZIONA_BIN_PATH"] = ENV["AZIONA_PATH"] + "/bin"
ENV["AZIONA_TERRAFORM_MODULES_PATH"] = ENV["AZIONA_PATH"] + "/terraform-modules"
ENV["AZIONA_TENANT_PATH"] = ENV["AZIONA_PATH"] + "/tenant"

if platform.system() == "Darwin":
  ENV["AZIONA_WORKSPACE_PATH"] = "/Users/" + getpass.getuser() + "/Documents/projects/azionaventures"
if platform.system() == "Linux":
  ENV["AZIONA_WORKSPACE_PATH"] = "/opt/project/azionaventures"

ENV["AZIONA_WORKSPACE_INFRASTRUCTURE"] = ENV["AZIONA_WORKSPACE_PATH"] + "/infrastructure"
ENV["AZIONA_WORKSPACE_AZIONACLI"] = ENV["AZIONA_WORKSPACE_PATH"] + "/aziona-cli"

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
    return parser


def scripts():
    import shutil

    source_dir = "./scripts/"
    dest_dir = ENV["AZIONA_BIN_PATH"] + "/"
    
    for file_name in os.listdir(source_dir):
        source = source_dir + file_name
        destination = dest_dir + file_name
        if os.path.isfile(source):
            shutil.copy(source, destination)
            print('copied', file_name)

def configurations():
    os.makedirs(f"{ENV['AZIONA_PATH']}", exist_ok=True)
    os.makedirs(f"{ENV['AZIONA_TENANT_PATH']}", exist_ok=True)
    os.makedirs(f"{ENV['AZIONA_WORKSPACE_PATH']}", exist_ok=True)
    os.makedirs(f"{ENV['AZIONA_BIN_PATH']}", exist_ok=True)
    os.makedirs(f"{ENV['AZIONA_TERRAFORM_MODULES_PATH']}", exist_ok=True)

    if os.path.isfile(ENV["AZIONA_ENV_PATH"]) is True:
        os.rename(ENV["AZIONA_ENV_PATH"], ENV["AZIONA_ENV_PATH"] + ".old")

    with open(ENV["AZIONA_ENV_PATH"], "w") as f:
        for key, value in ENV.items():
            f.write("export " + key + "=" + value + "\n")

    with open(ENV["AZIONA_ACTIVE_PERSISTENT_PATH"], "w") as f:
        f.write("")

    confirm = True if input("Add source in .bashrc or .zshrc [y,yes or n,no]: ").lower() in ["y","yes"] else False

    if confirm is False:
        return
    
    bashrc_path = os.getenv("HOME") + "/.bashrc"
    if os.path.isfile(bashrc_path) is True:
        with open(bashrc_path, "a") as f:
            f.write("\n" + RC)

    zshrc_path = os.getenv("HOME") + "/.zshrc"
    if os.path.isfile(zshrc_path) is True:
        with open(zshrc_path, "a") as f:
            f.write(RC)

def dependencies():
    def install_package(name):
        import pip
        import imp

        pip.main(["install", name])
        f, fname, desc = imp.find_module(name)
        return imp.load_module(name, f, fname, desc)

    import tempfile
    import platform

    try:
        import requests
    except:
        requests = install_package("requests")


    if platform.system() == "Darwin":
        if which("aws") is False:
            subprocess.check_call("brew install awscli", shell=True)
            subprocess.check_call("brew install aws-iam-authenticator", shell=True)

    if platform.system() == "Linux":
        if which("aws") is False:
            subprocess.check_call("""
                curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && \
                unzip awscliv2.zip && \
                sudo ./aws/install --bin-dir /usr/local/bin --install-dir /usr/local/aws-cli --update && \
                aws --version && \
                rm -Rf ./aws && \
                rm awscliv2.zip""", shell=True)
        if which("aws-iam-authenticator") is None:
            subprocess.check_call("""
                curl -O https://amazon-eks.s3.us-west-2.amazonaws.com/1.19.6/2021-01-05/bin/linux/amd64/aws-iam-authenticator && \
                chmod +x ./aws-iam-authenticator && \ 
                mv ./aws-iam-authenticator /usr/local/bin""", shell=True)

    response = requests.get("https://raw.githubusercontent.com/azionaventures/aziona-cli/main/bin/aziona-dependencies")

    file, filename = tempfile.mkstemp()
    with open(filename, "w") as f:
        f.write(response.text)

    command = f"python3 {filename}"

    subprocess.check_call(command, shell=True)

    os.close(file)

def main():
    args = argsinstance().parse_args()

    configurations()

    if args.only_scripts is False:
        dependencies()
        
    if args.only_depends is False:
        scripts()


    

if __name__ == "__main__":
    sys.exit(main())
