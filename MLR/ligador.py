import sys

def load(name):
	raw=open(name, "r")
	raw=raw.read()
	raw=raw.split("\n")
	code=[]
	for line in raw:
		code.append(line.split(" "))
	code.pop(-1)
	return code

#Open all the files
n_files=len(sys.argv)-1
if n_files==0:raise ValueError("Nenhum arquivo fornecido para ligar")
if n_files==1:raise ValueError("Impossível ligar um único arquivo")
if n_files==2:raise ValueError("Nenhum arquivo de saída definido")
names=sys.argv
names.pop(0)
nome=names[-1]
names.pop(-1)

#Generate code descriptors
files=[]
for file in names:files.append(load(file))

for file in files:
	cont=0
	for line in file:
		if len(line)==2: cont+=1
	file.append(cont)

soma=0
for file in files:soma+=file[-1]
if soma>0xfff//2: raise ValueError("Os códigos não cabem na memória.")

#Create bitmap to analyse compatibility and relocate
bitmap=[False]*(0xfff//2)
for file in files:
	size=file[-1]
	base=0
	while base+2*size<=0xfff and sum(bitmap[base//2:base//2+size])>0:
		base+=2
	if base+2*size>0xfff:
		raise ValueError("Não pode ser ligado, os arquivos se sobrepoem.")
	for line in file[:-1]:
		if len(line)==2:
			if int(line[0][0], 16)>=8:
				bitmap[base//2]=True
				for nline in file[:-1]:
					if len(nline)==5 and nline[3]=="'>" and nline[0][1:]==line[0][1:]: nline[0]=nline[0][0]+hex(base)[2:].zfill(3)
					if len(nline)==2 and nline[0][0]!="d" and nline[1][1:]==line[0][1:]: nline[1]=nline[1][0]+hex(base)[2:].zfill(3)
				line[0]=line[0][0]+hex(base)[2:].zfill(3)
				base+=2
			else:
				addr=int(line[0][1:], 16)
				if bitmap[addr//2]==True:
					raise ValueError("Não pode ser ligado, os arquivos se sobrepoem.")
				bitmap[addr//2]=True
				if addr==base: base+=2

#Generate entry points dictionary
entry_points={}
for file in files:
	for line in file[:-1]:
		if len(line)==5 and line[3]=="'>":
			entry_points[line[4]]=(line[0][1:], line[0][0]=="2")

#Substitute externals to entry points
for file in files:
	for line in file[:-1]:
		if len(line)==5 and line[3]=="'<" and line[4] in entry_points:
			ext=line[0][1:]
			for search in file[:-1]:
				if len(search)==2 and search[0][0] in ["5", "d"] and search[1][1:]==ext:
					soma=0
					if search[0][0]=="d": soma=8
					soma+=2*entry_points[line[4]][1]
					soma=hex(soma)[2]
					search[0]=soma+search[0][1:]
					search[1]=search[1][0]+entry_points[line[4]][0]
			line[0]=False

#Remove resolved external lines
for file in files:
	line=0
	while type(file[line])!=int:
		if file[line][0]==False:
			file.pop(line)
			line-=1
		line+=1

output=open(nome, "w")
for file in files:
	for line in file[:-1]:
		for item in line:
			output.write(item+" ")
		output.write("\n")
output.close()

print("Códigos ligados para "+nome)