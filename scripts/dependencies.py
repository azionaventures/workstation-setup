#!/usr/bin/env python3

import platform
import subprocess
import sys
from shutil import which
from distutils.version import LooseVersion

PYTHON_VERSION = LooseVersion(platform.python_version())
if PYTHON_VERSION < "3.6":
    raise RuntimeError("PY Version required >= 3.8")

DEPS = {
    "terraform": {
       "version": LooseVersion("1.1"),
       "install": {
        "ubuntu": (
            "curl -fsSL https://apt.releases.hashicorp.com/gpg | sudo apt-key add -",
            'sudo apt-add-repository "deb [arch=$(dpkg --print-architecture)] https://apt.releases.hashicorp.com $(lsb_release -cs) main"',
            "sudo apt install -y terraform=%version%",
        ),
        "darwin": (
            "brew install terraform@%version%",
            "brew link terraform@%version%"
        ),
       },
    },
    "kubectl": {
       "version": LooseVersion("1.23"),
       "install": {
        "ubuntu": (
            "curl -LO https://storage.googleapis.com/kubernetes-release/release/v%version%/bin/linux/amd64/kubectl",
            "chmod +x ./kubectl",
            "mv ./kubectl /usr/local/bin/kubectl",
        ),
        "darwin": (
            "brew install kubectl@%version%",
        ),
       },
    },
    "eksctl": {
       "version": LooseVersion("0.67.0"),
       "install": {
        "ubuntu": (
            "curl --location https://github.com/weaveworks/eksctl/releases/download/v%version%/eksctl_Linux_amd64.tar.gz | tar xz -C /tmp",
            "mv /tmp/eksctl /usr/local/bin",
        ),
        "darwin": (
            '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"',
            "brew tap weaveworks/tap",
            'brew install weaveworks/tap/eksctl@%version%'
        ),
       },
    },
    "kustomize": {
       "version": LooseVersion("4.0.5"),
       "install": {
        "ubuntu": (
            "curl -s https://raw.githubusercontent.com/kubernetes-sigs/kustomize/master/hack/install_kustomize.sh  | bash",
            "mv ./kustomize /usr/local/bin"
        ),
        "darwin": ("brew install kustomize",),
       },
    },
    "aws": {
       "version": LooseVersion("2"),
       "install": {
        "ubuntu": (
            'curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"',
            "unzip awscliv2.zip",
            "sudo ./aws/install"
        ),
        "darwin": (
            'curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"',
            "sudo installer -pkg AWSCLIV2.pkg -target"
        ),
       },
    },
    "aws-iam-authenticator": {
       "version": LooseVersion("1.19.6"),
       "install": {
        "ubuntu": (
            "curl -O https://amazon-eks.s3.us-west-2.amazonaws.com/%version%/2021-01-05/bin/linux/amd64/aws-iam-authenticator",
            "chmod +x ./aws-iam-authenticator",
            "mv ./aws-iam-authenticator /usr/local/bin",
        ),
        "darwin": ("brew install aws-iam-authenticator",),
       },
    },
    "jq": {
       "version": None,
       "install": {
        "ubuntu": ("sudo apt-get install -y jq",),
        "darwin": ("brew install jq",),
       },
    },
    "aziona": {
       "version": LooseVersion("0.1"),
       "install": {
        "ubuntu": ("pip3 install aziona==%version%",),
        "darwin": ("pip3 install aziona==%version%",),
       },
    }
}


import argparse

def argsinstance():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-y", "--yes",
        action="store_true",
        default=False,
        help="Accept request intput",
    )
    parser.add_argument(
        "-f", "--force",
        action="store_true",
        default=False,
        help="Force install packages",
    )
    parser.add_argument(
        "--skip",
        nargs="+",
        default=[],
        help="Skip packages",
    )
    return parser

def deps_exist(name: str):
    return which(name) is not None


def linux(args):
    def get_distribution():
        import csv

        dist = {}
        with open("/etc/os-release") as f:
            reader = csv.reader(f, delimiter="=")
            for row in reader:
                if row:
                    dist[row[0]] = row[1]

        print("Distribution: %s" % dist.get("NAME", "").lower())
        print("Release: %s" % dist.get("VERSION_ID", "").lower())
        print("Version: %s" % dist.get("VERSION", "").lower())
        return dist["NAME"].lower()


    if platform.system() != "Linux":
        return

    dist = get_distribution()

    if "ubuntu" in dist.lower():
        exec(distro="ubuntu", force_install=args.force, skip=args.skip)

    if "alpine" in dist.lower():
        exec(distro="alpine", force_install=args.force, skip=args.skip)


def darwin(args):
    if platform.system() != "Darwin":
        return

    exec(distro="darwin", force_install=args.force, skip=args.skip)


def windows():
    if platform.system() != "Windows":
        return
    raise RuntimeError("Install Unix o Linux os")


def exec(distro:str, force_install:bool = False, skip: list = []):
    if distro not in ("darwin", "ubuntu", "alpine"):
        raise RuntimeError("Not found scripts for yor os distribution")

    for key, data in DEPS.items():
        if deps_exist(key) and force_install is False:
            print(f"\n{key} installed.\nSuggestion version {data['version']}")
            continue

        if key in skip:
            print(f"{key} installation skipped")
            continue

        print(f"+ Package: {key}")
        print(f"  Version: {data['version']}")

        for cmd in data["install"][distro]:
            if data["version"]:
                cmd = cmd.replace("%version%", str(data["version"]))
            
            subprocess.check_call(cmd, shell=True)


def main():
    try:
        args = argsinstance().parse_args()
        linux(args)
        darwin(args)
        windows()
    except KeyboardInterrupt as e:
        pass

if __name__ == "__main__":
    sys.exit(main())