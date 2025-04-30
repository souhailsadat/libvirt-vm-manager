#!/usr/bin/env python2
# -*- coding: utf-8 -*- 

import libvirt
import os

''' **************************************************
Déclaration des fonctions et des structures de données
************************************************** '''

#Fonction qui liste les choix du menu principal
def listeChoix():
    print("     0) Informations sur la machine hyperviseur")
    print("     1) Lister les machines virtuelles")
    print("     2) Informations sur une machine virtuelle")
    print("     3) Opérations sur une machine virtuelle")
    print("     4) Visualiser une machine virtuelle")
    print("     5) Quitter")

#Dictionnaire qui contient les opérations possibles sur une machine virtuelle
operations = {
    1 : "démarrer",
    2 : "arrêter",
    3 : "forcer l'arrêt",
    4 : "suspendre",
    5 : "reprendre"
}
#Dictionnaire qui contient les états possibles d'une machine virtuelle
state = {
    libvirt.VIR_DOMAIN_RUNNING : "en cours d'exécution",
    libvirt.VIR_DOMAIN_PAUSED : "mise en pause",
    libvirt.VIR_DOMAIN_SHUTDOWN : "en arrêt",
    libvirt.VIR_DOMAIN_SHUTOFF : "éteinte"
}

#Fonction qui donne l'état d'une machine virtuelle
def etat(n):
    try:
        return state.get(n)
    except:
        return "éteinte"

''' ***********************************************************
Ne pas afficher les messages d'erreur de libvirt sur la console
*********************************************************** '''

#définir une fonction de gestion d'erreurs qui ne fait rien
def libvirt_callback(userdata, err): 
    pass 

#remplacer la fonction de gestion d'erreurs de libvirt qui affichent les messages
#d'erreur sur la console par une fonction qui ne fait rien afin de ne pas les afficher
libvirt.registerErrorHandler(f=libvirt_callback, ctx=None)

''' ********************************
ouvrir une connexion à l'hyperviseur
******************************** '''

#spécifier l'URI de connexion (dans notre cas une connexion locale en mode système)
conn = libvirt.open("qemu:///system")
if not conn:
    # si la connexion a échoué, afficher un message d'erreur et terminer le programme
    raise SystemExit("La connexion à l'hyperviseur a echoué !")

''' ********************
Boucle du menu principal
******************** '''

#afficher la liste des choix du menu principal
print("Programme de gestion des machines virtuelles ; veuillez entrer votre choix")
listeChoix()

choix = -1 #initialiser le choix
while (choix != 5): # Reboucler jusqu'à ce que le choix soit '5'

    try: 
        choix = int(raw_input("\nVotre choix : ")) #lire le choix entré par l'utilisateur
    except:
        choix = -1 #si le choix est erroné
    
    if(choix == 0): # si choix = 0 alors appeler les fonctions de libvirt qui affichent
                    # des informations sur l'hyperviseur et le host

        print("\n     Informations sur la machine hyperviseur :")
        print("     -----------------------------------------")
        print("     Nom de la machine hyperviseur : "+str(conn.getHostname()))
        print("     Nombre maximum de processus virtuels : "+str(conn.getMaxVcpus(None)))
        # info() retroune un tuple qui contient plusieurs informations
        print("     Modèle du processeur : "+str(conn.getInfo()[0]))
        print("     Taille de la RAM : "+str(conn.getInfo()[1])+" Mo")
        print("     Nombre de processeurs actifs : "+str(conn.getInfo()[2]))
        print("     Fréquence du processeur : "+str(conn.getInfo()[3])+" MHz")
        print("     Nombre de noeuds NUMA : "+str(conn.getInfo()[4]))
        print("     Nombre de processeurs: "+str(conn.getInfo()[5]))
        print("     Nombre de coeurs par processeurs : "+str(conn.getInfo()[6]))
        print("     Nombre de threads par coeur : "+str(conn.getInfo()[7]))

    elif(choix == 1): #Si le choix est 1, alors afficher la liste des machines virtuelles

        #récupère toutes les machines virtuelles
        list_VM = conn.listAllDomains() 
        #Longeur du plus long nom de machine virtuelle pour contrôler l'affichage
        max_len = len(max(list_VM, key = lambda d : len(d.name())).name())
        #constituer l'entête de la liste des VM 
        print("\n     Liste des machines virtuelles :\n")
        espace = min(max(max_len,20),20) 
        nom = "Nom".ljust(espace)
        head = " Id    "+nom+"    État                 "
        print("     "+head)
        print("     "+"".rjust(len(head),'-'))
        #Parcourir les machines virtuelles et les affciher dans la liste
        for dom in list_VM :
            id = str(dom.ID())
            #Si la machine est éteinte, le ID sera -1, alors afficher le caractère '-'
            if dom.ID() == -1:
                id = '-'
            print("      "+id.ljust(6)+dom.name().ljust(espace+4)+etat(dom.state()[0]))


    elif(choix == 2): #Si le choix est 2, afficher les informations sur une VM

        #Lire le nom de la machine virtuelle depuis la console
        nom = raw_input("     Introduire le nom d'une machine pour afficher" 
                        "ses informations : ")

        try:
            #rechercher la VM par nom
            dom = conn.lookupByName(nom) 

        except libvirt.libvirtError as e: 
            #Si la VM n'existe pas, afficher un message d'erreur
            print("     Erreur : Aucun domaine invité ne porte ce nom !")

        else: # si La machine virtuelle existe, alors afficher ses
              # informations en utilisant des fonctions de libvirt

            print("\n     Informations sur la machine '"+nom+"' :")
            print("     --------------------------------"+"".ljust(len(nom),'-'))
            print("          ID : "+str(dom.ID()))
            # la fonction info() retourne un tuple contenant plusieurs informations
            print("          État : "+etat(dom.info()[0]))
            print("          Maximum Mémoire RAM : "+str(dom.info()[1]/1024)+" Mo")
            print("          Mémoire RAM utilisée : "+str(dom.info()[2]/1024)+" Mo")
            print("          Nombre de CPUs virtuels : "+str(dom.info()[3]))
            print("          Temps CPU : "+str(dom.info()[4])+" ns")

            if not dom.isActive(): # Si la machine est éteinte, alors il n'est pas
                                   # possible de récupérer ses adresses IP
                print("          Adresse IP : indisponible !"
                      " Veuillez allumer la machine")

            else: #Si la machine est allumée, alors afficher ses adresses IP
                
                iffaces = {} # initialiser la structure qui contiendra les adresses
                try:
                    # Interroger "qemu-guest-agent" qui doit être installé et configuré 
                    # sur la machine virtuelle, s'il ne l'est pas, une exception sera
                    # lancée et doit être capturée dans le bloc try except
                    iffaces = dom.interfaceAddresses(
                        libvirt.VIR_DOMAIN_INTERFACE_ADDRESSES_SRC_AGENT, 0
                        )
                
                except libvirt.libvirtError as e:
                    # si Qemu Guest Agent n'est pas installé sur la machine virtuelle 
                    # ou s'il n'est pas connecté, alors signaler ceci par le message 
                    # d'erreur par défaut de libvirt
                    try:
                        print("          Adresse IP : indisponible !"
                                + (str(e)).split(":")[1])
                    except:
                        print("          Adresse IP : indisponible ! ")

                else: # sinon parcourir la structure retournée et extraire les adresses 
                      # IP, la structure est un dictionnaire ayant comme éléments
                      # les interfaces réseaux de la machine

                    adresse = "" #initialiser une chaîne pour concaténer les adresses IP
                    for (name, val) in iffaces.iteritems(): #pour chaque interface réseau
                        # extraire les champs d'adresses qui ne sont pas de type loopback
                        if val['addrs'] and name!='lo':
                            # Pour chaque adresse de l'interface réseau
                            for ipaddr in val['addrs']:
                                # extraire uniquement les adresses de type IPv4
                                if ipaddr['type'] == libvirt.VIR_IP_ADDR_TYPE_IPV4:
                                    # concaténer l'adresses à la chaîne
                                    adresse += ipaddr['addr'] + "  "
                    if adresse == "":
                        # si le résultat est vide, les adresses IP sont indisponibles
                        print("          Adresse IP : indisponible ! En cours de"
                              " recherche ou adresses non configurées")
                    else:
                        # afficher les adresses IP
                        print("          Adresse IP : "+str(adresse))
            
    elif(choix == 3): # Si le choix est 3, alors afficher un menu des opérations
                      # possibles à effectuer sur une machine virtuelle
        print("     Choisir l'opération à effectuer sur une machine virtuelle :")
        print("          1) Démarrer")
        print("          2) Arrêter")
        print("          3) Forcer l'arrêt")
        print("          4) Suspendre")
        print("          5) Reprendre")
        print("          6) Retour")
        try:
            # Récupérer le numéro de l'opération choisie
            op = int(raw_input("     Opération : "))
        except:
            # Traiter le cas d'un numéro erroné
            op = -1
        if(op in {1,2,3,4,5}):
            # Si le numéro introduit est valide, lire le nom de la machine virtuelle
            nom = raw_input("          Introduire le nom de la Machine que vous "
                                       "voulez " + operations.get(op) + " : ")
            try:
                # Rechercher la machine virtuelle par nom
                dom = conn.lookupByName(nom)
            except:
                # Si le nom n'existe pas, afficher un message d'erreur
                print("          Erreur : Aucun domaine invité ne porte ce nom !")
            else:

                if(op == 1): # L'opération : Démarrer une machine
                    try:
                        if(dom.state()[0]==libvirt.VIR_DOMAIN_SHUTOFF):
                            # Démarrer la machine seulement si elle est éteinte
                            dom.create()
                            print("          Machine démarrée avec succès")
                            print("          Pour visualiser la machine appuyer sur 4"
                                  " dans le menu principal")
                        else:
                            # Sinon, afficher un message d'erreur
                            print("          Erreur : La machine est déja en cours"
                                  " d'exécution !")
                    except libvirt.libvirtError as e:
                        # Afficher le message d'erreur d'une quelconque exception
                        print("          Erreur : "+str(e))

                elif(op == 2): # L'opération : Arrêter une machine
                    try:
                        if(dom.state()[0]==libvirt.VIR_DOMAIN_RUNNING):
                            # Arrêter la machine seulement si elle est allumée
                            dom.shutdown()
                            print("          Machine en cours d'arrêt")
                        else:
                             # Sinon, afficher un message d'erreur
                           print("          Erreur : La machine n'est pas en cours"
                                 " d'exécution !")
                    except libvirt.libvirtError as e:
                        # Afficher le message d'erreur d'une quelconque exception
                        print("          Erreur : "+str(e))

                elif(op == 3): # L'opération : Forcer l'arrêt d'une machine
                    try:
                        if(dom.state()[0]!=libvirt.VIR_DOMAIN_SHUTOFF):
                            # Forcer l'arrêt seulement si la machine n'est pas éteinte
                            dom.destroy()
                            print("          Machine arrêtée avec succès")
                        else:
                            # Sinon, afficher un message d'erreur
                            print("          Erreur : La machine est déja éteinte !")
                    except libvirt.libvirtError as e:
                        # Afficher le message d'erreur d'une quelconque exception
                        print("          Erreur : "+str(e))

                elif(op == 4): # L'opération : Mettre la machine en pause
                    try:
                        if(dom.state()[0]!=libvirt.VIR_DOMAIN_SHUTOFF):
                            # Suspendre la machine seulement si elle n'est pas éteinte
                            dom.suspend()
                            print("          Machine mise en pause avec succès")
                        else:
                            # Sinon, afficher un message d'erreur
                            print("          Erreur : La machine est éteinte !")
                    except libvirt.libvirtError as e:
                        # Afficher le message d'erreur d'une quelconque exception
                        print("          Erreur : "+str(e))

                elif(op == 5): # L'opération : Reprendre une machine suspendue
                    try:
                        if(dom.state()[0]==libvirt.VIR_DOMAIN_PAUSED):
                            # Reprendre la machine seulement si elle était en pause
                            dom.resume()
                            print("          Machine reprise avec succès")
                            print("          Pour visualiser la machine appuyer sur 4"
                                  " dans le menu principal")
                        else:
                            # Sinon, afficher un message d'erreur
                            print("          Erreur : La machine n'est pas en pause !")
                    except libvirt.libvirtError as e:
                        # Afficher le message d'erreur d'une quelconque exception
                        print("          Erreur : "+str(e))

        elif (op != 6): # Le choix n'est pas valide
            print("     choix erroné !")

    elif (choix == 4): # Si le choix est 4, alors ouvrir l'écran de la machine virtuelle 
                       # à l'aide de l'outil virt-viewer

        # Lire de la console le nom de la machine virtuelle à visualiser
        nom = raw_input("     Introduire le nom de la Machine virtuelle à visualiser : ")
        try:
            # Rechercher si nom de la machine virtuelle existe
            dom = conn.lookupByName(nom)
        except:
            # Si le nom n'existe pas, afficher un message d'erreur
            print("          Erreur : Aucun domaine invité ne porte ce nom !")
        else:
            try:
                # Si le nom existe, lancer une commande système qui ouvre virt-viewer
                os.system("virt-viewer "+nom+" &")
            except:
                # Afficher le message d'erreur si c'est le cas
                print("     Erreur : "+str(e))

    elif (choix != 5): #Le choix introduit dans le menu principal n'est pas valide
        
        print("Choix erroné ! veuillez entrer votre choix")
        listeChoix()

    if (choix in [0,1,2,3,4]): # Re-Afficher le menu principal

        wait = raw_input("\nAppuyer sur 'Enter' pour continuer...")
        print("\nMenu principal ; veuillez entrer votre choix")
        listeChoix()


conn.close() # Fermer la connexion avec l'hyperviseur
