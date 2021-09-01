#!/usr/bin/env python3

import sys
import argparse
import os
import platform
import getpass

EXPORT = ""

def default_config_path(company):
  if platform.system() == "Darwin":
    return "/Users/"+getpass.getuser()+"/Documents/projects/" + company + "/config"

  if platform.system() == "Linux":
    return "/opt/project/" + company + "/config"

def default_aziona_path():
  if platform.system() == "Darwin":
    return "/Users/"+getpass.getuser()+"/Documents/projects/azionaventures"

  if platform.system() == "Linux":
    return "/opt/project/azionaventures"

def add_to_export(name,value):
    global EXPORT
    EXPORT += f"export {name}={value}\n"
    os.environ[name] = value

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-e",
        "--env",
        required=True,
        type=str,
        help="Env tenant",
    )
    parser.add_argument(
        "-c",
        "--company",
        required=True,
        type=str,
        help="Env tenant",
    )
    parser.add_argument(
        "--config-path",
        required=False,
        default=None,
        type=str,
        help="Env tenant",
    )
    parser.add_argument(
        "--aziona-path",
        required=False,
        default=None,
        type=str,
        help="Env tenant",
    )

    args = parser.parse_args()

    if args.config_path is None:
        args.config_path = os.getenv("CONFIG_TENANT_SETTINGS_PATH", default_config_path(args.company))

    if args.aziona_path is None:
        args.aziona_path = os.getenv("AZIONAVENTURES_PATH", default_aziona_path())
    add_to_export("AZIONA_PATH",args.aziona_path)

    if os.path.isdir(args.config_path) is False:
        raise Exception("Tenant directory not found: " + args.config_path)

    tenant_path = "%s/%s-tenant-settings/%s/.env" % (args.config_path,args.company,args.env)
    if os.path.isfile(tenant_path) is False:
        raise Exception("Tenant file not exist: " + tenant_path)

    with open(tenant_path, "r") as f:
        for line in f.read().split("\n"):
            if line.startswith("#") or line == "":
                continue
            name, value = line.split("=")
            add_to_export(name,value)
    
    add_to_export("KUBECONFIG","/home/%s/.kube/eksctl/clusters/%s" % (getpass.getuser(),os.getenv("EKS_CLUSTER_NAME", "")))

    add_to_export("INFRASTRUCTURE_PATH", args.aziona_path + "/infrastructure")
    add_to_export("AZIONA_TERRAFORM_TEMPLATE_PATH", args.aziona_path + "/aziona-cli-terraform")

    global EXPORT
    EXPORT += "source " + args.aziona_path  + "/aziona-cli/venv/bin/activate > /dev/null 2>&1"

    print(EXPORT)


if __name__ == "__main__":
    sys.exit(main())