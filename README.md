# svg_to_ocg_pdf


===================================================

A quoi sert ce script ?

Dans ce package vous trouverez des fichiers permettant d'exécuter un script Python (svg_to_ocg_pdf.py)
Ce script permet d'exporter le contenu d'un fichier .SVG contenant des calques en un PDF contenant ces mêmes calques
Il est prévu pour gérer à la fois les calques, mais aussi le multi pages. 
Ainsi dans .SVG un calque de pages permet de définir les pages à exporter en PDF
Il est idéal notamment pour les modélistes qui veulent exporter leur patron mis en page dans Inkcape.


===================================================

ATTENTION - il y a plusieurs pré-requis pour l'utilisation de ce script car ce n'est pas une solution optimisée pour la diffusion :)
 
Pré-requis #1 :

	Pour pouvoir exécuter ce script vous devez avoir Python installé sur votre machine :
	Les librairies suivantes sont aussi nécessaires :
		lxml
		cairosvg
		pymupdf
	→ pip install lxml cairosvg pymupdf


Pré-requis #2 :

	Le dossier "gtk" doit toujours être au même niveau que le script svg_to_ocg_pdf.py
	Sinon, il faudra modifier le chemin dans les lignes 3-4 du script python.
	INFO : les fichiers de ce répertoire proviennent du ZIP ici : https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer


Pré-requis #3 :

	Votre fichier .SVG doit être spécifiquement paramétré pour que le script fonctionne (ou alors vous devrez adapter le code...)
 	 → voir explications ci-dessous


===================================================

Comment utiliser ce Script ?

	Dezipper tout le package et le déposer dans un répertoire "fixe"
	exemple : sous C:\Applis\ ou dans Mes Documents...
	Personnellement j'ai mettre un dossier "Applis" à la racine C:\ pour que tous les utilisateurs du PC puissent y avoir accès (notamment les exécutables portables)


---------------------------------------------------

Pour utiliser ce script vous pourrez le lancer via le fichier .bat 

Ce fichier .bat va devoir exécuter le script Python ; il est donc nécessaire dans un 1er temps de le modifier :

	Faire clic droit sur le fichier > "Modifier" :
	sur l'avant dernière ligne, remplacer le répertoire actuel ("C:\Applis\svg_to_ocg_pdf\svg_to_ocg_pdf.py") par le répertoire choisi pour héberger votre script python.
 
Une fois modifié, vous devrez positionner ce .bat dans le répertoire contenant le fichier .SVG à convertir


---------------------------------------------------

Paramétrage de votre fichier .SVG :

Le fichier SVG doit être paramétré pour avoir les mesures en mm !

	→ Vous pouvez régler cela dans les propriétés de document, dans le 1er onglet "display"
	D'ailleurs dans ce même onglet, vous verrez la valeur d'échelle appliquée (scale en anglais)
		→  si cette échelle n'est pas par défaut = 0,264585 alors il faudra modifier cette valeur dans les variables du script Python !
		
Le fichier SVG doit contenir un calque "Pages" contenant uniquement les cadres des pages qui seront les pages finale

Dans ce calque, vous devrez créer un rectangle par page et nommer chaque rectangle par le prefixe "page".

Pour les calques aui seront visibles dans le PDF final, vous devez les organiser et les nommer comme vous voulez.

Chaque calque dans Inkscape sera un calque dans le PDF.

Si vous masquez un calque dans Inkscape, il sera disponible dans le PDF mais masqué aussi par défaut.

Si vous masque un objet dans Inkscape, il ne sera pas exporté dans le PDF (c'est pratique pour les cadres et repères de pages notamment)

	→ un exemple de SVG est joint au package
	→ Vous pouvez modifier ces noms/valeurs dans les premières variables du script Python...
