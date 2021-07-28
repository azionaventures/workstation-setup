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

warn(){
        local msg=${1:-""}
        echo "[WARNING] ${msg}"
}

info(){
        local msg=${1:-""}
        echo "[INFO] ${msg}"
}

err(){
        local msg=${1:-""}
	local err_code=${2:-1}
        echo "[ERROR] ${msg}"
        exit ${err_code}
}

NAME=workstation-setup
PATH_CONF=$HOME/var/$NAME
PATH_BIN=$HOME/bin
DEFAULT_CONF_PATH=$PATH_CONF/default.cfg
PRIVATE_CONF_PATH=$PATH_CONF/private.cfg
CONFIGS_PATH=$PATH_CONF/conf.d

source ${DEFAULT_CONF_PATH}

if [ -f "${PRIVATE_CONF_PATH}" ] ; then
    	source ${PRIVATE_CONF_PATH}
fi

if [ -d ${CONFIGS_PATH} ] ; then
  for _config in $(ls ${CONFIGS_PATH})
  do
        source "${CONFIGS_PATH}/${_config}"
  done
fi