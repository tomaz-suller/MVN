import sys

def load(name):
	raw=open(name, "r")
	raw=raw.read()
	raw=raw.replace("\t", " ")
	raw=raw.split("\n")
	code=[]
	for line in raw:
		'''pure=line.split(";")
								if type(pure)==list: code.append(pure[0].split(" "))
								else: code.append(pure.split(" "))
								for elem in range(len(code[-1])):
									if code[-1][elem]==[]: code[-1].pop(elem)
								if code[-1]==['']: code.pop(-1)'''
		code.append(line.split(" "))
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

#Relocate each code using last addr of previous code as base
base=0
for file in files:
	for line in file[:-1]:
		if len(line)==2 and int(line[0][0],16)>=8:
			for nline in file[:-1]:
				if len(nline)==2 and nline[1][1:]==line[0][1:] and nline[0][0] in ["2", "a"] and nline[1][0] in ["0", "1", "2", "4", "5", "6", "7", "8", "9", "a", "b"]: nline[1]=nline[1][0]+hex(int(line[0][1:],16)+base)[2:].zfill(3)
			line[0]=line[0][0]+hex(int(line[0][1:],16)+base)[2:].zfill(3)
		elif len(line)==5 and int(line[0][0],16)==2: line[0]=line[0][0]+hex(int(line[0][1:],16)+base)[2:].zfill(3)
	#base=int(file[-3][0][1:],16)+2
	
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

#Write to the output file
output=open(nome, "w")
for file in files:
	for line in file[:-1]:
		for item in line:
			output.write(item+" ")
		output.write("\n")
output.close()

print("Códigos ligados para "+nome)