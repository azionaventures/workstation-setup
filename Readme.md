# Workstation 

### Install

    git clone https://github.com/azionaventures/workstation-setup.git

    cd workstation-setup
    
    make setup


Esegue solo l'installazione/aggiornamento degli scripts

    make update-scripts 

Esegue solo l'installazione delle dipendenze richieste

    make update-depends

### Usage

**Avviare una sessione aziona è necessario eseguire il comando che segue nel terminale:**

    # Start env
    aziona-active --company NOME --env ENV

    # Stop env
    aziona-deactive

*Dopo l'esecuzione di acitve o deactive è necessario ricaricare il terminale*

**Entrare in un container**:

    aziona-exec --pod-name NOME_P --container-name NOME_C

**Eseguire l'accesso**:

    aziona-ecr-login

**Eseguire infrastruttura**:

    aziona-infra -t TEMPLATE_NAME target1 target2 ...