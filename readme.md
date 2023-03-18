# spellsort

A script that will organize your disc images and prepare them for use with an Optical Drive Emulator (ODE). Namely, spellsort was designed for the Wizard and DocBrown ODE's for the FM-Towns Computers and the FM-Towns Marty console.

Wizard & DocBrown require adherence to a strict folder structure to work properly. The user must manually rename directories and write 'titles' for their games to be displayed by the ODE's boot menu. spellsort was made to simplify game library maintenance for ODE users. Just drop your disc image files on the SD card any way you like and run spellsort to ready your device.


## Usage

You need to have Python 3 installed on your OS. 

Extract the contents of this repo to the root of your Wizard/DocBrown SD card. Make sure you have either the "Wizard Spellbook" or "Marty's Almanac" in the '01' folder of your SD card already.


```
python spellsort.py --help
```
will display your options for using the script.


Disc image files associated with each other are assumed to have the same base name. 

e.g.: 
```
Pu-Li-Ru-La (Japan).ccd
Pu-Li-Ru-La (Japan).img
Pu-Li-Ru-La (Japan).sub
```
constitute a valid set. spellsort will not attempt to search for associated disc image files that don't have the same name.

Only sorting by alpha is supported. Customized file order would require the creation of a GUI, which is beyond the scope of this project.

Disc images must be uncompressed. spellsort will not automatically decompress zip/rar/etc archives.


Warning: spellsort will move all of the files on your SD card. If you are using your ODE's SD card as general storage, you can place your files in a folder called "ignore" at the root of the SD. This is the only folder whose contents will remain unchanged on a normal run. On a cleanup run, files that aren't used by Wizard will be moved to the 'ignore' folder.
