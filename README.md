# Virtual Machine Management Tool

A Python-powered CLI for managing KVM/libvirt virtual machines through an intuitive interactive menu, developed as part of a Virtualization course LAB.

## Features

- List all virtual machines with their status (running, paused, stopped)
- View detailed information about a specific VM (CPU, memory, IP addresses)
- Perform VM operations:
  - Start/shutdown VMs
  - Force stop
  - Suspend/resume
- Directly connect to VMs using virt-viewer
- View hypervisor host information

## Requirements

- Python 2.7.5
- libvirt Python bindings (`python-libvirt`)
- virt-viewer (for graphical console access)
- QEMU/KVM hypervisor

## Usage

```bash
# Install dependencies
$ sudo yum -y install qemu-kvm libvirt virt-install libvirt-dev python-libvirt virt-viewer

# Run the manager
$ python2 libvirt-vm-manager.py
Programme de gestion des machines virtuelles ; veuillez entrer votre choix
     0) Nom de la machine hyperviseur
     1) Lister les machines virtuelles
     2) démarrer une machine [donne un autre menu de choix de la machine à démarrer]
     3) Arrêter une machine [donne un autre menu de choix de la machine à arrêter]
     4) L’adresse IP d’une machine virtuelle donnée [donne un autre menu de choix]
     5) Quitter
Votre choix :
```
