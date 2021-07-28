# Workstation Setup

Install all depends and configuration for project maintenance

    sudo mkdir -p /opt/project/azionaventures 
    sudo setfacl -d -R -m u:$(whoami):rwx /opt/project
    sudo setfacl -R -m u:$(whoami):rwx /opt/project

    cd /opt/project/azionaventures 
    git clone https://github.com/azionaventures/workstation-setup.git
    cd workstation-setup
    
    make setup

### Customization

setup your osx

    export CONFIG_TENANT_SETTINGS_PATH=/PATH/TO/$ORGANIZATION_NAME-tenant-settings
    make setup
    source <(setkubeconfig $ORGANIZATION_NAME {cluster_environment})
    kubectl get pods

### Utils

    make update-scripts -> Esegue solo l'installazione/aggiornamento degli scripts
    make update-depends -> Esegue solo l'installazione delle dipendenze richieste