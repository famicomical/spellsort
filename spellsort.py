#spellsort.py

#This script searches CD-ROM images in every directory at the root of the Wizard SD card.
#If a directory contains multiple CD images, it will be split up. Subdirectories and the folder 'ignore' are ignored. 
#Valid directories are associated with their CD-ROM images and then numbered according to alphabetization.
#Finally, a valid title.txt is created in each directory that does not already have one.

#Just place spellsort.py at root of your Wizard SD card and run.

import os
import os.path as path
import argparse

parser= argparse.ArgumentParser(description='SpellSort program for Wizard/DocBrown CD drive emulators.')
parser.add_argument('--retitle', action='store_true', default=False, dest='retitle', help='will force title.txt generation for all folders')
parser.add_argument('--cleanup', action='store_true', default=False, dest='cleanup', help='moves all non-numeric files and folders to \'ignore\' folder, does nothing else')
parser.add_argument('--compile', action='store_true', default=False, dest='runme', help='executes RunMe.bat in folder \'01\' after terminating')
args=parser.parse_args()
retitling=args.retitle
cleaning= args.cleanup
runningbatch=args.runme

if not (path.isfile('.\Wizard.ini') or path.isfile('.\DocBrown.ini')):
	print('Run SpellSort from the root of your Wizard/DocBrown SD Card, or create .ini file')
	quit()

print('SpellSort for Wizard ODE')
wd= os.getcwd()

#words to exclude from title.txt
annoyingwords=[' (Japan)', '_hawked']

#files allowed to stay in SD root (lowercase)
exceptions = ['docbrown.ini','wizard.ini', 'spellsort.py', '01', 'ignore']

#extensions associated with CD image data
extlist= ['.iso','.cdi','.mdf','.img','.bin']


#Spells are a Folder/CD-ROM image pair.
class Spell:
	def __init__(self,folder,image):
		self.folder=folder
		self.image=image
	def __str__(self):
		return self.image+" in folder "+self.folder

	def swap(self,other):
		tempname=self.folder+'.tmp0'
		c=0
		while True:
			try:
				os.rename(path.join(wd,self.folder),path.join(wd,tempname))
				break
			except OSError:
				c+= 1
				tempname = tempname+(f".tmp{c}")
		os.rename(path.join(wd,other.folder), path.join(wd,self.folder))
		os.rename(path.join(wd,tempname), path.join(wd,other.folder))
		temp=self.folder
		self.folder=other.folder
		other.folder=temp

	def maketitle(self):
		with open(path.join(wd,self.folder,'title.txt'),'w') as title:
			text=str(self.image.encode('utf-8').decode('ascii', 'ignore'))
			for annoyingword in annoyingwords:
				if annoyingword in text:
					text=text.replace(annoyingword,'')
			if len(text)>127:
				text=text[0:127]
			title.write(text)

	def rename(self,newname):
		try:
			os.rename(path.join(wd,self.folder),path.join(wd,newname))
			self.folder=newname
			return True
		except OSError:
			return False

	def hastitle(self):
		return path.isfile(path.join(wd, self.folder, 'title.txt'))

#valid folder names
acceptable100= [str(x).zfill(2) for x in range(2,100)]
acceptable1k= [str(x).zfill(3) for x in range(100,1000)]
acceptable10k= [str(x).zfill(4) for x in range(1000,10000)]

#global to speed up folder creation
suff= 0


#creates a new folder and relocates the set of disc image files matching 'imagename' to the new folder
def newspell(foldername, imagename):
	global suff
	while True:
		try:
			newdir=f'newdir_{suff}'
			os.mkdir(path.join(wd,newdir))
			suff+=1
			break
		except OSError:
			suff+=1
	os.rename(path.join(wd,foldername,imagename),path.join(wd,newdir,imagename))
	filelist=[filename.lower() for filename in os.listdir(path.join(wd,foldername))]

	if imagename[-4:].lower()=='.mdf':
		if imagename[:-4]+'.mds' in filelist:
			os.rename(path.join(wd,foldername,imagename[:-4]+'.mds'),path.join(wd,newdir,imagename[:-4]+'.mds'))
	elif imagename[-4:].lower()=='.img':
		if imagename[:-4]+'.ccd' in filelist:
			os.rename(path.join(wd,foldername,imagename[:-4]+'.ccd'),path.join(wd,newdir,imagename[:-4]+'.ccd'))
		if  imagename[:-4]+'.sub' in filelist:
			os.rename(path.join(wd,foldername,imagename[:-4]+'.sub'),path.join(wd,newdir,imagename[:-4]+'.sub'))
	elif imagename[-4:].lower()=='.bin':
		if '(Track' in imagename:
			quit('Error: Redump multiple-track BIN/CUE image detected. \nBIN/CUE format is not supported. Please convert using a program like SBITools.')

	elif not imagename[-4:].lower() in extlist:
		quit('Error: invalid call to function newspell -- file extension must be in extlist')

	if imagename[:-4]+'.cue' in filelist:
		os.rename(path.join(wd,foldername,imagename[:-4]+'.cue'),path.join(wd,newdir,imagename[:-4]+'.cue'))

	return newdir


#ensures no collisions occur when renaming
def robust_rename(prefix, oldname):
	if prefix in oldname:
		oldname=oldname.replace(prefix+'_','')
	badname=prefix+'_'+oldname
	c=0
	while True:
		try:
			os.rename(path.join(wd,oldname),path.join(wd,badname))
			break
		except OSError:
			c+= 1
			badname = prefix+(f"_{c}")+oldname

#like robust rename but takes only absolute file paths
def robust_move(newpath, oldpath):
	c=0
	oldname= oldpath[oldpath.rfind('\\')+1:]
	ext=''
	if '.' in oldname:
		ext= oldname[oldname.rfind('.'):]
		oldname=oldname[:oldname.rfind('.')]
	while True:
		try:
			os.rename(oldpath,newpath)
			break
		except OSError:
			c+= 1
			newpath = newpath[:newpath.rfind('\\')+1]+oldname+(f" ({c})")+ext

#bubbles the contents of all subfolders into a root folder. arguments are absolute paths
def flatmap(parentfolder, subfolder):
	filelist=os.listdir(subfolder)
	if filelist:
		for file in filelist:
			if path.isdir(path.join(subfolder,file)):
				flatmap(subfolder, path.join(subfolder,file))
		bubbles=os.listdir(subfolder)
		for bubble in bubbles:
			robust_move(path.join(parentfolder,bubble),path.join(subfolder,bubble))
	os.rmdir(subfolder)

#cleanup routine puts everything in ignore folder that isn't used by Wizard or spellsort.py
def clean():
	if not path.exists(path.join(wd,'ignore')):
		os.mkdir(path.join(wd,'ignore'))
	thefiles=os.listdir()
	for file in thefiles:
		if not (file in acceptable100 or file in acceptable1k or file in acceptable10k or file.lower() in exceptions):
			robust_move(path.join(wd,'ignore',file),path.join(wd,file))

if cleaning:
	print('Cleaning up the root folder...')
	clean()	
	quit()



spells=[]
#Make a list of valid 'Spells'
#move loose disc image files into folders and split up folders that contain more than one image
for entry in os.scandir():
	if entry.is_file(follow_symlinks=False):
		if entry.name.isnumeric() and (int(entry.name)<10000 and (int(entry.name)>0)):
			if ((int(entry.name)<100) and (entry.name in acceptable100)) or ((int(entry.name)<1000) and (entry.name in acceptable1k)) or (entry.name in acceptable10k):
				robust_rename('unacceptable', entry.name)
		#look for disk image files
		for ext in extlist:
			if len(entry.name)>4 and entry.name[-4:].lower()==ext:
				spells+=[Spell(newspell('',entry.name), entry.name[:-4])]
				break
				
	#look inside each folder
	if entry.is_dir(follow_symlinks=False):
		if not entry.name=="01" and not entry.name=="ignore":
			files=os.listdir(entry.name)
			if not files:
				os.rmdir(path.join(wd,entry.name))

			#squash subfolders
			for folder in files:
				fpath=path.join(wd,entry.name,folder)
				if path.isdir(fpath):
					flatmap(path.join(wd,entry.name),fpath)
			#refresh files
			files=os.listdir(entry.name)

			key=[]
			for ext in extlist:
				key+=[i for i in files if len(i)>4 and ext in i[-4:].lower()]

			if len(key)<1:
				if entry.name.isnumeric():
					robust_rename('leftover', entry.name)

			#if there's more than one set of images per folder, split it up.
			elif len(key)>1:
				for k in range(len(key)):
					spells+=[Spell(newspell(entry.name,key[k]),key[k][-4:])]
				if os.listdir(entry.name):
					robust_rename('leftover', entry.name)
				else:
					os.rmdir(path.join(wd,entry.name))
			else:
				spells+=[Spell(entry.name, key[0][:-4])]


#format index into a folder name
def formati(index):
	index+=2
	if index<10:
		return str(index).zfill(2)
	else:
		return str(index)

#Here comes the sort
list.sort(spells, key=lambda x: x.image.lower())
folderlist= [f.folder for f in spells]

#Assign numbers to folders, generate title.txt
for i in range(len(spells)):
	newname=formati(i)
	if not spells[i].rename(newname):
		o=folderlist.index(newname)
		spells[i].swap(spells[o])

	if not spells[i].hastitle() or retitling:
		spells[i].maketitle()

if not runningbatch:
	print("Done! Don't forget to execute RunMe.bat in folder 01.")
	
else:
	import subprocess
	print('Calling RunMe.bat')
	os.chdir(path.join(wd,'01'))
	wd=os.getcwd()

	with open('RunMe.bat', 'r', encoding='utf-8') as runmefile:
		runscript= runmefile.readlines()
	if runscript[1]=="scan.exe \\ data\\\n":
		runscript[1]="scan.exe ..\\ data\\\n"
		with open('RunMe.bat', 'w', encoding='utf-8') as runmefile:
			runmefile.writelines(runscript)

	subprocess.call(path.join(wd,'RunMe.bat'))
	os.chdir('../')
	wd=os.getcwd()
	print("Done! Your SD card is ready for use")
