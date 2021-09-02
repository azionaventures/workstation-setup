#!/bin/bash

set -eE -o functrace

failure() {
  local lineno=$1
  local msg=$2
  echo "Failed at $lineno: $msg"
}
trap 'failure ${LINENO} "$BASH_COMMAND"' ERR

set -o pipefail
set -o nounset

AZIONA_PATH=${HOME}/.aziona
AZIONA_ENV_PATH=${AZIONA_PATH}/.env
AZIONA_BIN_PATH=${AZIONA_PATH}/bin
AZIONA_TERRAFORM_MODULES_PATH=${AZIONA_PATH}/terraform-modules
AZIONA_TENANT_PATH=${AZIONA_PATH}/tenant

if [ "$(uname)" == "Darwin" ]; then
  AZIONA_WORKSPACE_PATH=/Users/$(whoami)/Documents/projects/azionaventures
elif [ "$(expr substr $(uname -s) 1 5)" == "Linux" ]; then
  AZIONA_WORKSPACE_PATH=/opt/project/azionaventures
fi

AZIONA_WORKSPACE_INFRASTRUCTURE=${AZIONA_WORKSPACE_PATH}/infrastructure
AZIONA_WORKSPACE_AZIONACLI=${AZIONA_WORKSPACE_PATH}/aziona-cli

ONLY_SCRIPTS=false
ONLY_DEPENDS=false

showHelp() {
  echo "Configurazione ed installazione delle dipendenze per lo sviluppo Devops"
  echo
  echo "Syntax: setup.sh [ -u;--update-scripts | -h;--help ]"
  echo "options:"
  echo "-s | --only-scripts  : Installazione/Aggiornamento degli script aziona"
  echo "-d | --only-depends  : Installazione dipendenze (k8s, awscli, iam-authenticator, docker, terraform) "
  echo "-h | --help          : Print help"
  echo
  exit 0
}

depends() {
  if [ ${ONLY_SCRIPTS} == true ] ; then
    return
  fi



  if [ "$(which aws)" == "" ] ; then
    if [ "$(uname)" == "Darwin" ]; then
      brew install awscli 
    elif [ "$(expr substr $(uname -s) 1 5)" == "Linux" ]; then
      if [ ! -d $HOME/.aws ] ; then
        mkdir -v $HOME/.aws
        touch $HOME/.aws/config
        touch $HOME/.aws/credentials
      fi
      curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
      unzip awscliv2.zip
      sudo ./aws/install --bin-dir /usr/local/bin --install-dir /usr/local/aws-cli --update
      aws --version
      rm -Rf ./aws
      rm awscliv2.zip
    fi
  else
    echo "AWS CLI installed.\nSuggestion version 2"
  fi

  if [ "$(which aws-iam-authenticator)" == "" ] ; then
    if [ "$(uname)" == "Darwin" ]; then
      brew install aws-iam-authenticator
    elif [ "$(expr substr $(uname -s) 1 5)" == "Linux" ]; then  
      curl -O https://amazon-eks.s3.us-west-2.amazonaws.com/1.19.6/2021-01-05/bin/linux/amd64/aws-iam-authenticator
      chmod +x ./aws-iam-authenticator
      mv ./aws-iam.authenticator /usr/local/bin
    fi
  else
    echo "aws-iam-authenticator installed."
  fi

  # Install depends from aziona-cli
  (cd /tmp && curl -O https://raw.githubusercontent.com/azionaventures/aziona-cli/main/bin/aziona-dependencies)
  chmod +x /tmp/aziona-dependencies 
  sudo /tmp/aziona-dependencies
}

_mkdir() {
  local _path=${1:-}
  if [ ! -d "${_path}" ] ; then
    echo "[INFO] Create path: ${_path}" 
    mkdir -pv "${_path}"
  fi
}

_add_to_file() {
  local _str=${1}
  local _filepath=${2}

  if [ ! -f "${_filepath}" ] ; then
    return
  fi

  if [ "$(grep -w "${_str}" ${_filepath})" == "" ] ; then
    echo "${_str}" >> ${_filepath}
  fi
}

configuration() {
  if [ ${ONLY_DEPENDS} == true ] ; then
    return
  fi
  
  echo "[INFO] Exec install with user $(whoami)" 

  _mkdir "${AZIONA_PATH}"
  _mkdir "${AZIONA_TENANT_PATH}"
  _mkdir "${AZIONA_WORKSPACE_PATH}"
  _mkdir "${AZIONA_BIN_PATH}"
  _mkdir "${AZIONA_TERRAFORM_MODULES_PATH}"

  # CREATE ENV FILE
  if [ ! -f ${AZIONA_ENV_PATH} ] ; then
    touch "${AZIONA_ENV_PATH}"
  fi
  _add_to_file "export AZIONA_PATH=${AZIONA_PATH}" "${AZIONA_ENV_PATH}"
  _add_to_file "export AZIONA_ENV_PATH=${AZIONA_ENV_PATH}" "${AZIONA_ENV_PATH}"
  _add_to_file "export AZIONA_TENANT_PATH=${AZIONA_TENANT_PATH}" "${AZIONA_ENV_PATH}"
  _add_to_file "export AZIONA_WORKSPACE_PATH=${AZIONA_WORKSPACE_PATH}" "${AZIONA_ENV_PATH}"
  _add_to_file "export AZIONA_WORKSPACE_INFRASTRUCTURE=${AZIONA_WORKSPACE_INFRASTRUCTURE}" "${AZIONA_ENV_PATH}"
  _add_to_file "export AZIONA_WORKSPACE_AZIONACLI=${AZIONA_WORKSPACE_AZIONACLI}" "${AZIONA_ENV_PATH}"
  _add_to_file "export AZIONA_BIN_PATH=${AZIONA_BIN_PATH}" "${AZIONA_ENV_PATH}"
  _add_to_file "export AZIONA_TERRAFORM_MODULES_PATH=${AZIONA_TERRAFORM_MODULES_PATH}"  "${AZIONA_ENV_PATH}"

  # CONFIGURE .bashrc
  if [ -f ~/.bashrc ] ; then
    _add_to_file "# AZIONA CONFIG" ~/.bashrc
    _add_to_file "source \${HOME}/.aziona/.env" ~/.bashrc
    _add_to_file "export PATH=\$PATH:\$AZIONA_BIN_PATH"  ~/.bashrc
  fi

  # CONFIGURE .zshrc
  if [ -f ~/.zshrc ] ; then
    _add_to_file "# AZIONA CONFIG" ~/.zshrc
    _add_to_file "source \${HOME}/.aziona/.env" ~/.zshrc
    _add_to_file "export PATH=\$PATH:\$AZIONA_BIN_PATH"  ~/.zshrc
  fi

  # ADD SCRIPTS
  cp -Rv scripts/* "$AZIONA_BIN_PATH"
  chmod -R 750 "$AZIONA_BIN_PATH"

  # ADD TERRAFORM MODULES AZIONA
  if [ ! -d "${AZIONA_TERRAFORM_MODULES_PATH}/aziona-terraform-modules" ] ; then
    git clone https://github.com/azionaventures/aziona-terraform-modules.git "${AZIONA_TERRAFORM_MODULES_PATH}/aziona-terraform-modules"
  fi
}

parser() {
  options=$(getopt -l "help,only-scripts,only-depends" -o "h s d" -a -- "$@")
  eval set -- "$options"

  while true
      do
      case $1 in
          -h|--help)
              showHelp #@TODO: creare funzione help
              ;;
          -s|--only-scripts)
              ONLY_SCRIPTS=true
              ;;
          -d|--only-depends)
              ONLY_DEPENDS=true
              ;;
          --)
              shift
              break;;
      esac
      shift
  done
  shift "$(($OPTIND -1))"
}

main(){
  parser "$@"
  configuration
  depends
}

main "$@"
