#!/bin/bash
echo -e "Ajout d'une interface de consultation des audits pour SUSE Manager."
echo -e "Ce script doit être lance depuis le serveur SUSE Manager Server."
echo
  function suma_required_packages {
while true; do
   read -p "Installation des paquets Python3 et Python3-Flask necessaire au bon fonctionnement? (y/n) " yn
   case $yn in
      [Yy]* )
	  echo -e "Installation en cours."
          zypper -n in python3 python3-Flask
	  break
	  ;;
      [Nn]* )
          echo
	  echo "Etape annulee";
	  echo
	  break
	  ;;
          * ) echo "Please answer yes (y) or no (n).";;
   esac
done
  }
  function suma_webui_audit {
while true; do
   read -p "Lancement de la Web UI SUSE Manager pour la consultation d'audits? (y/n) " yn
   case $yn in
      [Yy]* )
	  echo -e "Execution en cours."
          export FLASK_APP=app.py
          flask run --host=0.0.0.0 --cert=/root/ssl-build/RHN-ORG-TRUSTED-SSL-CERT --key=/root/ssl-build/RHN-ORG-PRIVATE-SSL-KEY
	  break
	  ;;
      [Nn]* )
          echo
	  echo "Etape annulee";
	  echo -e "Fin."
	  echo
	  break
	  ;;
          * ) echo "Please answer yes (y) or no (n).";;
   esac
done
  }
suma_required_packages
suma_webui_audit
