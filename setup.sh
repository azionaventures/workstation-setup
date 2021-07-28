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
  
  if [ "$(which kubectl)" == "" ] ; then
    echo "[INFO] Install K8S"
    if [ "$(uname)" == "Darwin" ]; then
      brew install kubectl
    elif [ "$(expr substr $(uname -s) 1 5)" == "Linux" ]; then
      sudo curl -LO https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl  
      sudo chmod +x ./kubectl 
      sudo mv ./kubectl /usr/local/bin/kubectl 
      sudo curl -s https://raw.githubusercontent.com/kubernetes-sigs/kustomize/master/hack/install_kustomize.sh  | bash  
      sudo mv ./kustomize /usr/local/bin 
    fi
  else
    echo "[INFO] K8S already installed"
  fi

  if [ "$(which eksctl)" == "" ] ; then
    echo "[INFO] Install eksctl"
    if [ "$(uname)" == "Darwin" ]; then
      brew tap weaveworks/tap
      brew install eksctl
    elif [ "$(expr substr $(uname -s) 1 5)" == "Linux" ]; then
      sudo curl --silent --location https://github.com/weaveworks/eksctl/releases/latest/download/eksctl_$(uname -s)_amd64.tar.gz | tar xz -C /tmp  
      sudo mv /tmp/eksctl /usr/local/bin
    fi
  else
    echo "[INFO] eksctl already installed"
  fi

  if [ "$(which aws)" == "" ] ; then
    echo "Manual install: AWS CLI version 2"
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
    echo "[INFO] AWS CLI version 2 already installed"
  fi

  if [ "$(which aws-iam-authenticator)" == "" ] ; then
    echo "Manual install: aws-iam-authenticator"
    if [ "$(uname)" == "Darwin" ]; then
      brew install aws-iam-authenticator
    elif [ "$(expr substr $(uname -s) 1 5)" == "Linux" ]; then  
      curl -o aws-iam-authenticator https://amazon-eks.s3.us-west-2.amazonaws.com/1.19.6/2021-01-05/bin/linux/amd64/aws-iam-authenticator
      chmod +x ./aws-iam-authenticator
      mkdir -p $HOME/bin && cp ./aws-iam-authenticator $HOME/bin/aws-iam-authenticator && export PATH=$PATH:$HOME/bin
      echo 'export PATH=$PATH:$HOME/bin' >> ~/.bashrc
      echo 'export PATH=$PATH:$HOME/bin' >> ~/.zshrc
      rm aws-iam-authenticator
    fi
  else
    echo "[INFO] aws-iam-authenticator already installed"
  fi
  
  
  if [ "$(which docker)" == "" ] ; then
    echo "Manual install: Docker"
    if [ "$(uname)" == "Darwin" ]; then
      brew install docker 
    elif [ "$(expr substr $(uname -s) 1 5)" == "Linux" ]; then
      sudo apt-get update
      sudo apt-get install \
        apt-transport-https \
        ca-certificates \
        curl \
        gnupg \
        lsb-release
      curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
      echo \
      "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
      $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
      sudo apt-get update
      sudo apt-get install docker-ce docker-ce-cli containerd.io

      if [ ! -f /usr/bin/docker-compose ] ; then
        sudo curl -L "https://github.com/docker/compose/releases/download/1.28.5/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        sudo chmod +x /usr/local/bin/docker-compose
        sudo ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose
      else
        echo "[INFO] docker-compose already installed"
      fi
    fi
  else
    echo "[INFO] Docker already installed"
  fi

  if [ "$(which terraform)" == "" ] ; then
    echo "Manual install: Terraform v0.13"
    if [ "$(uname)" == "Darwin" ]; then
      brew install terraform@0.13
      brew link terraform@0.13
    elif [ "$(expr substr $(uname -s) 1 5)" == "Linux" ]; then  
      curl -fsSL https://apt.releases.hashicorp.com/gpg | sudo apt-key add -
      sudo apt-add-repository "deb [arch=amd64] https://apt.releases.hashicorp.com $(lsb_release -cs) main"
      sudo apt install terraform=0.13.3
    fi
  else
    echo "[INFO] Terraform v0.13.3 already installed"
  fi
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
