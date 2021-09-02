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

NAME=workstation-setup

if [ "$(uname)" == "Darwin" ]; then
  PATH_WORK=/Users/$(whoami)/Documents/projects
elif [ "$(expr substr $(uname -s) 1 5)" == "Linux" ]; then
  PATH_WORK=/opt/project
fi
PATH_CONF=$HOME/var/$NAME
PATH_BIN=$HOME/bin
PATH_AZIONA=$HOME/.aziona
PATH_AZIONA_TERRAFORM_MODULE=${PATH_AZIONA}/terraform-modules
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

  # Install depends from aziona-cli
  (cd /tmp && curl -O https://raw.githubusercontent.com/azionaventures/aziona-cli/main/bin/aziona-dependencies)
  chmod +x /tmp/aziona-dependencies 
  /tmp/aziona-dependencies
}

configuration() {
  if [ ${ONLY_DEPENDS} == true ] ; then
    return
  fi
  
  echo "[INFO] Exec install with user $(whoami)" 

  if [ ! -d $PATH_WORK ] ; then
    echo "[INFO] Create path work" 
    mkdir -pv $PATH_WORK
  fi 

  # ADD CONFIG SCRIPTS  
  echo "[INFO] Copy config scripts"
  if [ ! -d "$PATH_CONF" ] ; then
    mkdir -pv "$PATH_CONF"
  fi 
  cp -Rv conf.d "$PATH_CONF"
  cp -v default.cfg "$PATH_CONF"
  cp -v base.sh "$PATH_CONF"
  chmod -R 754 "$PATH_CONF"

  # ADD SCRIPTS  
  echo "[INFO] Copy scripts"
  if [ ! -d "$PATH_BIN" ] ; then
    mkdir -pv "$PATH_BIN"
  fi 
  cp -Rv scripts/* "$PATH_BIN"
  chmod -R 754 "$PATH_BIN"

  if [ ! -d "${PATH_AZIONA}" ] ; then
    mkdir -pv "${PATH_AZIONA}"
  fi

  if [ ! -d "${PATH_AZIONA_TERRAFORM_MODULE}" ] ; then
    git clone https://github.com/azionaventures/aziona-terraform-modules.git "${PATH_AZIONA_TERRAFORM_MODULE}"
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
