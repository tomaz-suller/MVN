from eventos import *
from motor_de_eventos import *
import argparse
import sys

#Constantes
EOF="EOF"
DESCARTAVEIS=[" ", "\t"]
CONTROLE=["\n"]
RESERVADAS=["#", "@", "&", ";",
			"/", "=", "'",
			">", "<"]
LETRAS_HEXA=["A", "B", "C", "D", "E", "F", "a", "b", "c", "d", "e", "f"]
OPERADORES=["JP", "JZ", "JN", "LV", "AD", "SB", "ML", "DV", "LD", "MM", "SC", "RS", "HM", "GD", "PD", "OS", "K", "$"]
VERMELHO="\u001b[31m"
VERDE="\u001b[32m"
BRANCO="\u001b[37m"
AMARELO="\u001b[33m"
ESTADO_FINAL="P1"
ESTADO_INICIAL="P0"

#Hiperparâmetros

parser=argparse.ArgumentParser(description="Hiperparâmetros do interpretador de ghun")
parser.add_argument("input", 				action="store", type=str, 					help="Caminho para o arquivo a ser interpretado.")
parser.add_argument("-o", "--output",		action="store", type=str, 	required=False, help="Caminho para o arquivo a ser gerado. Default: igual ao arquivo de entrada.", default="")
parser.add_argument("-v", "--verbosidade",	action="store", type=int, 	required=False, help="Verboidade da interpretação. Quanto maior, mais informações são mostradas durante o reconhecimento e interpretação. Default: 0", default=0)
parser.add_argument("-t", "--tokens",	 	action="store_true",		required=False, help="Se ativo, mostra os tokens provenientes da análise léxica.", default=False)
parser.add_argument("-st", "--sintatico", 	action="store_false",		required=False, help="Se ativo, não executa a análise sintática, apenas a léxica.", default=True)
parser.add_argument("-sm", "--semantico", 	action="store", type=int,	required=False, help="Indica quanto da análise semantica deve ser feita. 0 para não fazer, 1 para analisar as definições de variáveis, 2 para analisar os usos de variáveis e 3 ou maior para realizar toda a geração de código. Default: 3", default=3)
parser.add_argument("-g", "--gerar",	 	action="store_false",		required=False, help="Se ativo, não executa a escrita do código no arquivo de saída.", default=True)
parser.add_argument("-b", "--base",		 	action="store", type=int,	required=False, help="Endereço base do código a ser gerado em hexadecimal, para o caso de não estar definido no código de entrada. Default: 0.", default=0)
parser.add_argument("-a", "--absoluto",	 	action="store_false",		required=False, help="Se ativo, o código gerado não será relocável, para caso não seja definido no código de entrada.", default=True)
args=parser.parse_args()

TOKENS=args.tokens
SINTATICO=args.sintatico
SEMANTICO=args.semantico
GERAR=args.gerar
VERBOSIDADE=args.verbosidade
CODIGO=args.input
CODIGO_OUT= CODIGO.split(".")[0] if args.output=="" else args.output
BASE=args.base
ABSOLUTO=args.absoluto

#Tipos
#				 arquivo=["file"]
#				   linha=["linha", "eof"]
#			  caracteres=["util", "descartavel", "controle"]
#	    caracteres_uteis=["letra", "digito", "especial"]
#caracteres_descartaveis=["delimitador"]
#				 palavra=["terminal", "n-terminal", "especial", "reservada"]

#Código

if VERBOSIDADE>1:
	print("Iniciando análise léxica\n-----------------------------")

#Motor para separar arquivo em linhas
def le_arquivo(evento, extra_params=()):
	try:
		arquivo=open(evento)
	except:
		if VERBOSIDADE>-1:
			print(f"{VERMELHO}O arquivo {evento} não existe.")
		exit()
	conteudo=arquivo.read()
	linhas=conteudo.split("\n")
	linhas=[Evento(indice, "linha", (linhas[indice]+"\n")) for indice in range(len(linhas))]
	for indice in range(len(linhas)-1):
		linhas[indice].proximo=linhas[indice+1]
	eof=Evento(0, "eof", (EOF))
	linhas[-1].proximo=eof
	return linhas[0]

arquivo_entrada=Evento(0, "file", (CODIGO))

sistemas_de_arquivos=MotorDeEventos(arquivo_entrada, {"file": le_arquivo})

linha=sistemas_de_arquivos.roda_um_evento()

#Motor para separar linha em caracteres
def le_linha(evento, chave_base):
	linha=list(evento)
	caracteres=[]
	for indice in range(len(linha)):
		if linha[indice] in DESCARTAVEIS:
			tipo="descartavel"
		elif linha[indice] in CONTROLE:
			tipo="controle"
		else:
			tipo="util"
		caracteres.append(Evento(chave_base+indice, tipo, (linha[indice])))
		if indice!=0: caracteres[-2].proximo=caracteres[-1]
	return caracteres[0]

def add_eof(evento, chave_base):
	return Evento(chave_base, "eof", EOF)

filtro_ascii=MotorDeEventos(linha, {"linha": le_linha, 
									"eof":add_eof})

carac=filtro_ascii.roda_um_evento((0))

#Motor para classificar caracteres uteis
def categoriza_ascii_util(evento, chave_base):
	if evento.isalpha():
		tipo="letra"
	elif evento.isnumeric():
		tipo="digito"
	else:
		tipo="especial"
	return Evento(chave_base, tipo, evento)

def categoriza_ascii_descartavel(evento, chave_base):
	return Evento(chave_base, "delimitador", evento)

def categoriza_ascii_controle(evento, chave_base):
	return Evento(chave_base, "controle", evento)

categorizador_ascii=MotorDeEventos(carac, {"util": categoriza_ascii_util, 
										   "descartavel": categoriza_ascii_descartavel,
										   "controle": categoriza_ascii_controle,
										   "eof": add_eof})

while filtro_ascii.fila_de_eventos!=None:
	carac=filtro_ascii.roda_um_evento((categorizador_ascii.ultima_chave()+1))
	categorizador_ascii.insere_na_fila(carac)

carac=categorizador_ascii.roda_um_evento((0))

linha=1

#Motor para agrupar caracter em palavras
def categoriza_lexico_letra(evento, extra_params):
	global linha
	chave_base, palavra_acumulada, tipo, dentro_de_aspas=extra_params
	if tipo=="":
		return (None,(chave_base, evento, "identificador", dentro_de_aspas))
	elif tipo=="identificador":
		return (None,(chave_base, palavra_acumulada+evento, "identificador", dentro_de_aspas))
	elif tipo=="numero":
		if evento in LETRAS_HEXA:
			return (None,(chave_base, palavra_acumulada+evento, "numero", dentro_de_aspas))
		if VERBOSIDADE>-1:
			print(f"{VERMELHO}Palavra mal formada na linha {linha}.")
		exit()
	elif tipo=="especial":
		if palavra_acumulada[0]=='"':
			return (None,(chave_base, palavra_acumulada+evento, "especial", dentro_de_aspas))
		return (Evento(chave_base, "especial", palavra_acumulada), 
					  (chave_base+1, evento, "identificador", dentro_de_aspas))

def categoriza_lexico_digito(evento, extra_params):
	chave_base, palavra_acumulada, tipo, dentro_de_aspas=extra_params
	if tipo=="":
		return(None, (chave_base, evento, "numero", dentro_de_aspas))
	elif tipo=="identificador":
		return(None, (chave_base, palavra_acumulada+evento, "identificador", dentro_de_aspas))
	elif tipo=="numero":
		return(None, (chave_base, palavra_acumulada+evento, "numero", dentro_de_aspas))
	elif tipo=="especial":
		if palavra_acumulada[0]=='"':
			return (None,(chave_base, palavra_acumulada+evento, "especial", dentro_de_aspas))
		return (Evento(chave_base, "especial", palavra_acumulada), 
					  (chave_base+1, evento, "numero", dentro_de_aspas))

def categoriza_lexico_especial(evento, extra_params):
	chave_base, palavra_acumulada, tipo, dentro_de_aspas=extra_params
	if evento=='"': dentro_de_aspas=not dentro_de_aspas
	if tipo=="":
		if evento in OPERADORES and not dentro_de_aspas:
			return (Evento(chave_base, "especial", evento), 
					  (chave_base+1, "", "", dentro_de_aspas))
		return (None, (chave_base, evento, "especial", dentro_de_aspas))
	elif tipo=="identificador":
		if evento in OPERADORES and not dentro_de_aspas:
			identifi=Evento(chave_base, "identificador", palavra_acumulada)
			operador=Evento(chave_base+1, "especial", evento)
			identifi.proximo=operador
			return (identifi, 
					  (chave_base+2, "", "", dentro_de_aspas))
		return (None, (chave_base, palavra_acumulada+evento, "identificador", dentro_de_aspas))
	elif tipo=="numero":
		return (Evento(chave_base, "numero", palavra_acumulada), 
					  (chave_base+1, evento, "especial", dentro_de_aspas))
	elif tipo=="especial":
		if evento in OPERADORES and not dentro_de_aspas:
			especial=Evento(chave_base, "especial", palavra_acumulada)
			operador=Evento(chave_base+1, "especial", evento)
			especial.proximo=operador
			return (especial, 
					  (chave_base+2, "", "", dentro_de_aspas))
		return (None, (chave_base, palavra_acumulada+evento, "especial", dentro_de_aspas))

def categoriza_lexico_delimitador(evento, extra_params):
	chave_base, palavra_acumulada, tipo, dentro_de_aspas=extra_params
	if tipo=="":
		return (None, (chave_base, "", "", dentro_de_aspas))
	else:
		return (Evento(chave_base, tipo, palavra_acumulada), 
					  (chave_base+1, "", "", dentro_de_aspas))

def categoriza_lexico_controle(evento, extra_params):
	global linha
	linha+=1
	chave_base, palavra_acumulada, tipo, dentro_de_aspas=extra_params
	if tipo=="":
		return (Evento(chave_base, "controle", evento), 
					  (chave_base+1, "", "", dentro_de_aspas))
	else:
		ult_evento=Evento(chave_base, tipo, palavra_acumulada)
		ult_evento.proximo=Evento(chave_base+1, "controle", evento)
		return (ult_evento,
			   (chave_base+2, "", "", dentro_de_aspas))

def categoriza_lexico_eof(evento, extra_params):
	chave_base, palavra_acumulada, tipo, dentro_de_aspas=extra_params
	return (Evento(chave_base, "eof", EOF), (chave_base+1, "", "", dentro_de_aspas))

categorizador_lexico=MotorDeEventos(carac, {"letra":categoriza_lexico_letra,
											"digito": categoriza_lexico_digito,
											"especial": categoriza_lexico_especial,
											"delimitador": categoriza_lexico_delimitador,
											"controle": categoriza_lexico_controle,
											"eof": categoriza_lexico_eof})

while categorizador_ascii.fila_de_eventos!=None:
	carac=categorizador_ascii.roda_um_evento((categorizador_lexico.ultima_chave()+1))
	categorizador_lexico.insere_na_fila(carac)

palavra=categorizador_lexico.roda_um_evento((0, "", "", False))

while palavra[0]==None:
	palavra=categorizador_lexico.roda_um_evento(palavra[1])

#Motor para categorizar e agrupar palvras em reservadas
def recategoriza_identificador(evento, extra_params):
	chave_base, reservada, indice=extra_params
	if evento in RESERVADAS:
		return (Evento(chave_base, "reservada", evento),
				(chave_base+1, "", None))
	elif evento in OPERADORES:
		return (Evento(chave_base, "instrucao", evento),
				(chave_base+1, "", None))
	else:
		return (Evento(chave_base, "n-terminal", evento),
				(chave_base+1, "", None))

def recategoriza_especial(evento, extra_params):
	chave_base, reservada, indice=extra_params
	if evento in RESERVADAS:
		return (Evento(chave_base, "reservada", evento),
				(chave_base+1, "", None))
	elif evento in OPERADORES:
		return (Evento(chave_base, "instrucao", evento),
				(chave_base+1, "", None))
	elif evento[0]=='"' and evento[-1]=='"':
		return (Evento(chave_base, "terminal", evento[1:-1]),
				(chave_base+1, "", None))
	else:
		return (Evento(chave_base, "n-terminal", evento),
				(chave_base+1, "", None))

def recategoriza_numero(evento, extra_params):
	chave_base, reservada, indice=extra_params
	return (Evento(chave_base, "terminal", evento),
			(chave_base+1, "", None))

def recategoriza_controle(evento, extra_params):
	chave_base, reservada, indice=extra_params
	return (Evento(chave_base, "controle", evento),
			(chave_base+1, "", None))

def recategoriza_eof(evento, extra_params):
	chave_base, reservada, indice=extra_params
	return (Evento(chave_base, "eof", evento),
			(chave_base+1, "", None))

recategrorizador_lexico=MotorDeEventos(palavra[0], {"identificador": recategoriza_identificador, 
													"especial": recategoriza_especial,
													"numero": recategoriza_numero,
													"controle": recategoriza_controle,
													"eof": recategoriza_eof})

while categorizador_lexico.fila_de_eventos!=None:
	palavra=categorizador_lexico.roda_um_evento(palavra[1])
	while palavra[0]==None:
		palavra=categorizador_lexico.roda_um_evento(palavra[1])
	recategrorizador_lexico.insere_na_fila(palavra[0])

palavra=recategrorizador_lexico.roda_um_evento((0, "", None))

while palavra[0]==None:
	palavra=recategorizador_lexico.roda_um_evento(palavra[1])

pilha_retorno=[]
linha=1
erro_sintatico=False

#Retorno das rotinas (estado, contador, transicao)
def fim_codigo(simbolo, estado): 
	global VERBOSIDADE
	if VERBOSIDADE>1:
		print("Terminando o programa")
	return estado

def base(simbolo, estado): 
	global VERBOSIDADE
	if VERBOSIDADE>1:
		print("Encontrado endereço base")
	return estado

def rotulo(simbolo, estado): 
	global VERBOSIDADE
	if VERBOSIDADE>1:
		print("Encontrado novo rotulo")
	return estado

def entry_point(simbolo, estado): 
	global VERBOSIDADE
	if VERBOSIDADE>1:
		print("Encontrado um entry point")
	return estado

def external(simbolo, estado): 
	global VERBOSIDADE
	if VERBOSIDADE>1:
		print("Encontrado um external")
	return estado

def instrucao(simbolo, estado): 
	global VERBOSIDADE
	if VERBOSIDADE>1:
		print("Encontrada uma instrução")
	return estado

def num_hex(simbolo, estado): 
	global VERBOSIDADE
	if VERBOSIDADE>1:
		print("Encontrado um número hexadecimal")
	return estado

def num_dec(simbolo, estado): 
	global VERBOSIDADE
	if VERBOSIDADE>1:
		print("Encontrado um número decimal")
	return estado

def num_oct(simbolo, estado): 
	global VERBOSIDADE
	if VERBOSIDADE>1:
		print("Encontrado um número octal")
	return estado

def num_bin(simbolo, estado): 
	global VERBOSIDADE
	if VERBOSIDADE>1:
		print("Encontrado um número binário")
	return estado

def num_asc(simbolo, estado): 
	global VERBOSIDADE
	if VERBOSIDADE>1:
		print("Encontrado um número ASCII")
	return estado

def faz_nada(simbolo, estado):
	return estado

def checa_hex(simbolo, estado):
	global erro_sintatico, linha
	try:
		int(simbolo, 16)
	except:
		print(f"{VERMELHO}Erro na linha {linha}. {simbolo} não é hexadecimal.{BRANCO}")
		erro_sintatico=True
	return estado

def checa_dec(simbolo, estado):
	global erro_sintatico, linha
	try:
		int(simbolo, 10)
	except:
		print(f"{VERMELHO}Erro na linha {linha}. {simbolo} não é decimal.{BRANCO}")
		erro_sintatico=True
	return estado

def checa_oct(simbolo, estado):
	global erro_sintatico, linha
	try:
		int(simbolo, 8)
	except:
		print(f"{VERMELHO}Erro na linha {linha}. {simbolo} não é octal.{BRANCO}")
		erro_sintatico=True
	return estado

def checa_bin(simbolo, estado):
	global erro_sintatico, linha
	try:
		int(simbolo, 2)
	except:
		print(f"{VERMELHO}Erro na linha {linha}. {simbolo} não é binário.{BRANCO}")
		erro_sintatico=True
	return estado

def checa_asc(simbolo, estado):
	global erro_sintatico, linha
	if len(simbolo)>2:
		print(f"{VERMELHO}Erro na linha {linha}. {simbolo} tem mais que dois dígitos.{BRANCO}")
		erro_sintatico=True
	return estado

transicoes_sintatico={
			"P0":{
				"controle"			: (faz_nada, "P0"),
				"#"					: (fim_codigo, "P2"),
				"@"					: (base, "P3"),
				"&"					: (base, "P3"),
				"n-terminal"		: (rotulo, "P11"),
				">"					: (entry_point, "P13"),
				"<"					: (external, "P13"),
				";"					: (faz_nada, "P10"),
				"instrucao"			: (instrucao, "P12")
			},
			"P1":{
				"controle"			: (faz_nada, "P1"),
				"else"				: (faz_nada, "PANICO")
			},
			"P2":{
				"n-terminal"		: (faz_nada, "P1"),
				"else"				: (faz_nada, "PANICO")
			},
			"P3":{
				"/"					: (num_hex, "P4"),
				"="					: (num_dec, "P5"),
				"@"					: (num_oct, "P6"),
				"#"					: (num_bin, "P7"),
				"'"					: (num_asc, "P8"),
				"else"				: (faz_nada, "PANICO")
			},
			"P4":{
				"terminal"			: (checa_hex, "P9"),
				"else"				: (faz_nada, "PANICO")
			},
			"P5":{
				"terminal"			: (checa_dec, "P9"),
				"else"				: (faz_nada, "PANICO")
			},
			"P6":{
				"terminal"			: (checa_oct, "P9"),
				"else"				: (faz_nada, "PANICO")
			},
			"P7":{
				"terminal"			: (checa_bin, "P9"),
				"else"				: (faz_nada, "PANICO")
			},
			"P8":{
				"n-terminal"		: (checa_asc, "P9"),
				"else"				: (faz_nada, "PANICO")
			},
			"P9":{
				";"					: (faz_nada, "P10"),
				"controle"			: (faz_nada, "P0"),
				"else"				: (faz_nada, "PANICO")
			},
			"P10":{
				"controle"			: (faz_nada, "P0"),
				"terminal"			: (faz_nada, "P10"),
				"n-terminal"		: (faz_nada, "P10"),
				"#"					: (faz_nada, "P10"),
				"@"					: (faz_nada, "P10"),
				"&"					: (faz_nada, "P10"),
				";"					: (faz_nada, "P10"),
				"/"					: (faz_nada, "P10"),
				"="					: (faz_nada, "P10"),
				"'"					: (faz_nada, "P10"),
				">"					: (faz_nada, "P10"),
				"<"					: (faz_nada, "P10"),
				"instrucao"			: (faz_nada, "P10"),
				"else"				: (faz_nada, "PANICO")
			},
			"P11":{
				"instrucao"			: (instrucao, "P12"),
				"else"				: (faz_nada, "PANICO")
			},
			"P12":{
				"/"					: (num_hex, "P4"),
				"="					: (num_dec, "P5"),
				"@"					: (num_oct, "P6"),
				"#"					: (num_bin, "P7"),
				"'"					: (num_asc, "P8"),
				"n-terminal"		: (faz_nada, "P14"),
				"else"				: (faz_nada, "PANICO")
			},
			"P13":{
				"n-terminal"		: (faz_nada, "P14"),
				"else"				: (faz_nada, "PANICO")
			},
			"P14":{
				";"					: (faz_nada, "P10"),
				"controle"			: (faz_nada, "P0"),
				"else"				: (faz_nada, "PANICO")
			},
			"PANICO":{
				"controle"			: (faz_nada, "P0"),
				"else"				: (faz_nada, "PANICO")
			}
}

#Máquina de estados que faz a análise siintática do código
def sintatico_generico(evento, busca, extra_params):
	global transicoes_sintatico
	global linha
	global pilha_retorno
	chave_base, atual=extra_params
	if VERBOSIDADE>2:
		print(f"No estado {atual}, recebi {evento}, que foi buscado como {busca}, e a pilha está assim: {pilha_retorno}")
	try:
		rotina, proximo=transicoes_sintatico[atual][busca]
	except:
		rotina=None
		operacao, param=transicoes_sintatico[atual]["else"]
	if rotina==None:
		estado_novo=operacao(evento, param)
		if param=="PANICO":
			if VERBOSIDADE>1:
				print("Encontrado um erro, indo para o estado de pânico.")
			return (chave_base+1, "PANICO")
		return sintatico_generico(evento, busca, (chave_base, estado_novo))
	else:
		estado = rotina(evento, proximo)
		return (chave_base+1, estado)

def sintatico_terminal(evento, extra_params):
	return sintatico_generico(evento, "terminal", extra_params)

def sintatico_nterminal(evento, extra_params):
	return sintatico_generico(evento, "n-terminal", extra_params)

def sintatico_reservada(evento, extra_params):
	return sintatico_generico(evento, evento, extra_params)

def sintatico_instrucao(evento, extra_params):
	return sintatico_generico(evento, "instrucao", extra_params)

def sintatico_controle(evento, extra_params):
	global linha
	linha+=1
	return sintatico_generico(evento, "controle", extra_params)

def sintatico_eof(evento, extra_params):
	chave_base, atual=extra_params
	return (chave_base+1, None, atual)

sintatico=MotorDeEventos(palavra[0], {"terminal":sintatico_terminal,
									  "n-terminal":sintatico_nterminal,
									  "reservada":sintatico_reservada,
									  "instrucao":sintatico_instrucao,
									  "controle":sintatico_controle,
									  "eof":sintatico_eof})

while recategrorizador_lexico.fila_de_eventos!=None:
	palavra=recategrorizador_lexico.roda_um_evento(palavra[1])
	while palavra[0]==None:
		palavra=recategrorizador_lexico.roda_um_evento(palavra[1])
	sintatico.insere_na_fila(palavra[0])

if TOKENS:
	c=sintatico.fila_de_eventos
	while c.proximo!=None:
		print(str(c.parametros)+"->"+c.tipo+", "+str(c.chave_ordenacao))
		c=c.proximo
	print(str(c.parametros)+"->"+c.tipo+", "+str(c.chave_ordenacao))

if not SINTATICO:
	sys.exit()

if VERBOSIDADE>1:
	print("\nIniciando análise sintática\n-----------------------------")

backup=sintatico.fila_de_eventos

palavra=sintatico.roda_um_evento((0, ESTADO_INICIAL))

while sintatico.fila_de_eventos!=None:
	palavra=sintatico.roda_um_evento(palavra)

chave_base, atual, estado=palavra
if erro_sintatico:
	sys.exit()

if VERBOSIDADE>0:
	print(f"{VERDE}O código está sintaticamente correto.{BRANCO}")

linha=1
endereco=BASE
relocavel=ABSOLUTO
rotulos={}
externals=set()
erro_vars=False
codigo_para_base={"/":16, "=":10, "@":8, "#":2}

def faz_nada(simbolo, estado, contexto):
	return estado, contexto

def adiciona_external(simbolo, estado, contexto):
	global externals, erro_vars
	if contexto.pop(-1)=="<":
		if simbolo in rotulos:
			erro_vars=True
			if VERBOSIDADE>-1:
				print(f"{VERMELHO}Erro na linha {linha}. Já existe rotulo com nome {simbolo}.{BRANCO}")
		else:
			externals.add(simbolo)
	return estado, contexto

def adiciona_rotulo(simbolo, estado, contexto):
	global rotulos, linha, externals, erro_vars, endereco, relocavel
	if simbolo in set.union(externals, set(rotulos.keys())):
		if simbolo in externals:
			erro_vars=True
			if VERBOSIDADE>-1:
				print(f"{VERMELHO}Erro na linha {linha}. Já existe external com nome {simbolo}.{BRANCO}")
		elif simbolo in rotulos:
			if VERBOSIDADE>-1:
				print(f"{AMARELO}Aviso na linha {linha}. Já existe rótulo com nome {simbolo}, tem certeza que deseja sobreescrever?{BRANCO}")
	else:
		rotulos[simbolo]=(endereco, relocavel)
	return estado, contexto

def define_endereco(simbolo, estado, contexto):
	global endereco, relocavel
	if contexto:
		tipo_int=contexto.pop(-1)
		instrucao=contexto.pop(-1)
		if instrucao=="$":
			if tipo_int=="'":
				endereco+=2*ord(simbolo[0])*0x100+ord(simbolo[1])-2
			else:
				endereco+=2*int(simbolo, codigo_para_base[tipo_int])-2
		elif instrucao in ["@", "&"]:
			relocavel=instrucao=="&"
			if tipo_int=="'":
				endereco=ord(simbolo[0])*0x100+ord(simbolo[1])-2
			else:
				endereco=int(simbolo, codigo_para_base[tipo_int])-2
	return estado, contexto

def atualiza_endereco(simbolo, estado, contexto):
	global endereco
	endereco+=2
	return estado, contexto

def adiciona_id(simbolo, estado, contexto):
	contexto.append(simbolo)
	return estado, contexto

transicoes_semantico_1={
			"P0":{
				"controle"			: (faz_nada, "P0"),
				"#"					: (faz_nada, "P2"),
				"@"					: (adiciona_id, "P3"),
				"&"					: (adiciona_id, "P3"),
				"n-terminal"		: (adiciona_rotulo, "P11"),
				">"					: (adiciona_id, "P13"),
				"<"					: (adiciona_id, "P13"),
				";"					: (faz_nada, "P10"),
				"instrucao"			: (adiciona_id, "P12")
			},
			"P1":{
				"controle"			: (faz_nada, "P1")
			},
			"P2":{
				"n-terminal"		: (faz_nada, "P1")
			},
			"P3":{
				"/"					: (adiciona_id, "P4"),
				"="					: (adiciona_id, "P5"),
				"@"					: (adiciona_id, "P6"),
				"#"					: (adiciona_id, "P7"),
				"'"					: (adiciona_id, "P8")
			},
			"P4":{
				"terminal"			: (define_endereco, "P9")
			},
			"P5":{
				"terminal"			: (define_endereco, "P9")
			},
			"P6":{
				"terminal"			: (define_endereco, "P9")
			},
			"P7":{
				"terminal"			: (define_endereco, "P9")
			},
			"P8":{
				"n-terminal"		: (define_endereco, "P9")
			},
			"P9":{
				";"					: (faz_nada, "P10"),
				"controle"			: (atualiza_endereco, "P0")
			},
			"P10":{
				"controle"			: (atualiza_endereco, "P0"),
				"terminal"			: (faz_nada, "P10"),
				"n-terminal"		: (faz_nada, "P10"),
				"#"					: (faz_nada, "P10"),
				"@"					: (faz_nada, "P10"),
				"&"					: (faz_nada, "P10"),
				";"					: (faz_nada, "P10"),
				"/"					: (faz_nada, "P10"),
				"="					: (faz_nada, "P10"),
				"'"					: (faz_nada, "P10"),
				">"					: (faz_nada, "P10"),
				"<"					: (faz_nada, "P10"),
				"instrucao"			: (faz_nada, "P10")
			},
			"P11":{
				"instrucao"			: (adiciona_id, "P12")
			},
			"P12":{
				"/"					: (adiciona_id, "P4"),
				"="					: (adiciona_id, "P5"),
				"@"					: (adiciona_id, "P6"),
				"#"					: (adiciona_id, "P7"),
				"'"					: (adiciona_id, "P8"),
				"n-terminal"		: (faz_nada, "P14")
			},
			"P13":{
				"n-terminal"		: (adiciona_external, "P14")
			},
			"P14":{
				";"					: (faz_nada, "P10"),
				"controle"			: (atualiza_endereco, "P0")
			}
}

transicoes_semantico=transicoes_semantico_1

#Máquina de estados que coleta as variáveis, vetores, rótulos e externals
def semantico_generico(evento, busca, extra_params):
	global transicoes_semantico
	global linha
	global pilha_retorno
	chave_base, atual, contexto=extra_params
	if VERBOSIDADE>2:
		print(f"No estado {atual}, recebi {evento}, que foi buscado como {busca}, e a pilha está assim: {pilha_retorno}")
	rotina, proximo=transicoes_semantico[atual][busca]
	estado, contexto_novo = rotina(evento, proximo, contexto)
	return (chave_base+1, estado, contexto_novo)

def semantico_terminal(evento, extra_params):
	return semantico_generico(evento, "terminal", extra_params)

def semantico_nterminal(evento, extra_params):
	return semantico_generico(evento, "n-terminal", extra_params)

def semantico_reservada(evento, extra_params):
	return semantico_generico(evento, evento, extra_params)

def semantico_instrucao(evento, extra_params):
	return semantico_generico(evento, "instrucao", extra_params)

def semantico_controle(evento, extra_params):
	global linha
	linha+=1
	return semantico_generico(evento, "controle", extra_params)

def semantico_eof(evento, extra_params):
	chave_base, atual, contexto=extra_params
	return (chave_base+1, None, atual)

if SEMANTICO<1:
	sys.exit()

if VERBOSIDADE>1:
	print("\nIniciando análise semântica 1\n-----------------------------")

semantico_1=MotorDeEventos(backup, {"terminal":semantico_terminal,
								    "n-terminal":semantico_nterminal,
								    "reservada":semantico_reservada,
									"instrucao":semantico_instrucao,
								    "controle":semantico_controle,
								    "eof":semantico_eof})

palavra=semantico_1.roda_um_evento((0, ESTADO_INICIAL, []))
while semantico_1.fila_de_eventos!=None:
	palavra=semantico_1.roda_um_evento(palavra)

linha=1

def confere_rotulo(simbolo, estado, contexto):
	global rotulos, variaveis, vetores, externals, linha, erro_vars
	if simbolo not in set.union(externals, set(rotulos.keys())):
		erro_vars=True
		if VERBOSIDADE>-1:
			print(f"{VERMELHO}Erro na linha {linha}. Rótulo {simbolo} não foi definido.{BRANCO}")
	return estado, contexto

def tira_id(simbolo, estado, contexto):
	contexto.pop(-1)
	return estado, contexto

transicoes_semantico_2={
			"P0":{
				"controle"			: (faz_nada, "P0"),
				"#"					: (faz_nada, "P2"),
				"@"					: (faz_nada, "P3"),
				"&"					: (faz_nada, "P3"),
				"n-terminal"		: (faz_nada, "P11"),
				">"					: (faz_nada, "P13"),
				"<"					: (faz_nada, "P13"),
				";"					: (faz_nada, "P10"),
				"instrucao"			: (faz_nada, "P12")
			},
			"P1":{
				"controle"			: (faz_nada, "P1")
			},
			"P2":{
				"n-terminal"		: (faz_nada, "P1")
			},
			"P3":{
				"/"					: (faz_nada, "P4"),
				"="					: (faz_nada, "P5"),
				"@"					: (faz_nada, "P6"),
				"#"					: (faz_nada, "P7"),
				"'"					: (faz_nada, "P8")
			},
			"P4":{
				"terminal"			: (faz_nada, "P9")
			},
			"P5":{
				"terminal"			: (faz_nada, "P9")
			},
			"P6":{
				"terminal"			: (faz_nada, "P9")
			},
			"P7":{
				"terminal"			: (faz_nada, "P9")
			},
			"P8":{
				"n-terminal"		: (faz_nada, "P9")
			},
			"P9":{
				";"					: (faz_nada, "P10"),
				"controle"			: (faz_nada, "P0")
			},
			"P10":{
				"controle"			: (faz_nada, "P0"),
				"terminal"			: (faz_nada, "P10"),
				"n-terminal"		: (faz_nada, "P10"),
				"#"					: (faz_nada, "P10"),
				"@"					: (faz_nada, "P10"),
				"&"					: (faz_nada, "P10"),
				";"					: (faz_nada, "P10"),
				"/"					: (faz_nada, "P10"),
				"="					: (faz_nada, "P10"),
				"'"					: (faz_nada, "P10"),
				">"					: (faz_nada, "P10"),
				"<"					: (faz_nada, "P10"),
				"instrucao"			: (faz_nada, "P10")
			},
			"P11":{
				"instrucao"			: (faz_nada, "P12")
			},
			"P12":{
				"/"					: (faz_nada, "P4"),
				"="					: (faz_nada, "P5"),
				"@"					: (faz_nada, "P6"),
				"#"					: (faz_nada, "P7"),
				"'"					: (faz_nada, "P8"),
				"n-terminal"		: (confere_rotulo, "P14")
			},
			"P13":{
				"n-terminal"		: (confere_rotulo, "P14")
			},
			"P14":{
				";"					: (faz_nada, "P10"),
				"controle"			: (faz_nada, "P0")
			}
}

transicoes_semantico=transicoes_semantico_2

#Máquina de estados que confere se as chamadas às variáveis, vetores e rótulos está condizente
semantico_2=MotorDeEventos(backup, {"terminal":semantico_terminal,
								    "n-terminal":semantico_nterminal,
								    "reservada":semantico_reservada,
									"instrucao":semantico_instrucao,
								    "controle":semantico_controle,
								    "eof":semantico_eof})

palavra=semantico_2.roda_um_evento((0, ESTADO_INICIAL, []))

if SEMANTICO<2:
	sys.exit()

if VERBOSIDADE>1:
	print("\nIniciando análise semântica 2\n-----------------------------")

while semantico_2.fila_de_eventos!=None:
	palavra=semantico_2.roda_um_evento(palavra)

if erro_vars:
	if VERBOSIDADE>-1:
		print(f"{VERMELHO}Compilação foi interrompida devido aos erros apresentados.{BRANCO}")
	sys.exit()

if VERBOSIDADE>0:
	print(f"{VERDE}As variáveis foram geradas corretamente.{BRANCO}")

#Cria a string que conterá o código compilado e escreve seu preâmbulo
codigo_mvn=""
codigo_lst=""

linha=0
endereco=BASE
contexternal=0
relocavel=ABSOLUTO

def escreve_lst_entrada(simbolo, estado, contexto):
	global codigo_lst
	codigo_lst+=desempilha_contexto(contexto+[simbolo])
	return estado, []

def gera_valor(simbolo, estado, contexto):
	tipo_int=contexto[-1]
	contexto.append(simbolo)
	if tipo_int=="'":
		if len(simbolo)==1:
			contexto.append(ord(simbolo[0]))
		else:
			contexto.append(ord(simbolo[0])*0x100+ord(simbolo[1]))
	else:
		contexto.append(int(simbolo, codigo_para_base[tipo_int]))
	return estado, contexto

def desempilha_contexto(contexto):
	saida=f";"
	while contexto:
		saida+=f" {contexto.pop(0)}"
	return saida

def gera_codigo_de_valor(simbolo, estado, contexto):
	global codigo_mvn, codigo_lst, endereco, relocavel, OPERADORES
	valor=contexto.pop(-1)
	instrucao=contexto[-3]
	if instrucao in ["@", "&"]:
		endereco=valor-2
		relocavel=instrucao=="&"
		codigo_lst+=desempilha_contexto(contexto+[simbolo])
	elif instrucao=="$":
		if valor==0 and VERBOSIDADE>-1:
			print(f"{AMARELO}Você tem certeza de que sabe o que está fazendo? Na linha {linha} você criou um espaço de memória com tamanho 0...{BRANCO}")
		preambulo=8*relocavel
		for end in range(endereco, endereco+2*valor, 2):
			linha_gerada=f"{hex(preambulo)[2:]}{hex(end)[2:].zfill(3)} 0000"
			codigo_mvn+=f"{linha_gerada}\n"
			codigo_lst+=linha_gerada+desempilha_contexto(contexto+[simbolo])
		endereco+=2*valor-2
	elif instrucao=="K":
		linha_gerada=f"{hex(8*relocavel)[2:]}{hex(endereco)[2:].zfill(3)} {hex(valor)[2:].zfill(4)}"
		codigo_mvn+=f"{linha_gerada}\n"
		codigo_lst+=linha_gerada+desempilha_contexto(contexto+[simbolo])
	else:
		linha_gerada=f"{hex(8*relocavel)[2:]}{hex(endereco)[2:].zfill(3)} {hex(OPERADORES.index(instrucao))[2:]}{hex(valor)[2:].zfill(3)}"
		codigo_mvn+=f"{linha_gerada}\n"
		codigo_lst+=linha_gerada+desempilha_contexto(contexto+[simbolo])
	endereco+=2
	return estado, []

def gera_codigo_de_rotulo(simbolo, estado, contexto):
	global codigo_mvn, codigo_lst, endereco, relocavel, OPERADORES, rotulos, externals, contexternal, linha
	rotulo=contexto[-1]
	instrucao=contexto[-2]
	if instrucao=="<":
		linha_gerada=f"4{hex(contexternal)[2:].zfill(3)} 0000"
		codigo_mvn+=f"{linha_gerada}\n"
		codigo_lst+=linha_gerada+desempilha_contexto(contexto+[simbolo])
		contexternal+=1
		endereco-=2
	elif instrucao==">":
		linha_gerada=f"{hex(2*rotulos[rotulo][1])[2:]}{hex(endereco)[2:].zfill(3)} {hex(rotulos[rotulo][0])[2:].zfill(4)}"
		codigo_mvn+=f"{linha_gerada}\n"
		codigo_lst+=linha_gerada+desempilha_contexto(contexto+[simbolo])
	elif instrucao in ["@", "&"]:
		endereco=rotulo-2
		relocavel=instrucao=="&"
		codigo_lst+=desempilha_contexto(contexto+[simbolo])
	elif instrucao=="$":
		if VERBOSIDADE>-1:
			print(f"{AMARELO}Você tem certeza de que sabe o que está fazendo? Na linha {linha} você criou um espaço de memória com tamanho de um rótulo...{BRANCO}")
		preambulo=8*relocavel+5*(rotulo in externals)+2*rotulos[rotulo][1]
		for end in range(endereco, endereco+2*rotulos[rotulo][0], 2):
			linha_gerada=f"{hex(preambulo)[2:]}{hex(end)[2:].zfill(3)} 0000"
			codigo_mvn+=f"{linha_gerada}\n"
			codigo_lst+=linha_gerada+desempilha_contexto(contexto+[simbolo])
		endereco+=2*rotulos[rotulo][0]-2
	elif instrucao=="K":
		if rotulo in externals:
			preambulo=8*relocavel+5
		else:
			preambulo=8*relocavel+2*rotulos[rotulo][1]
		linha_gerada=f"{hex(preambulo)[2:]}{hex(endereco)[2:].zfill(3)} {hex(rotulos[rotulo][0])[2:].zfill(4)}"
		codigo_mvn+=f"{linha_gerada}\n"
		codigo_lst+=linha_gerada+desempilha_contexto(contexto+[simbolo])
	else:
		if rotulo in externals:
			preambulo=8*relocavel+5
		else:
			preambulo=8*relocavel+2*rotulos[rotulo][1]
		linha_gerada=f"{hex(preambulo)[2:]}{hex(endereco)[2:].zfill(3)} {hex(OPERADORES.index(instrucao))[2:]}{hex(rotulos[rotulo][0])[2:].zfill(3)}"
		codigo_mvn+=f"{linha_gerada}\n"
		codigo_lst+=linha_gerada+desempilha_contexto(contexto+[simbolo])
	endereco+=2
	return estado, []

transicoes_semantico_3={
			"P0":{
				"controle"			: (escreve_lst_entrada, "P0"),
				"#"					: (adiciona_id, "P2"),
				"@"					: (adiciona_id, "P3"),
				"&"					: (adiciona_id, "P3"),
				"n-terminal"		: (adiciona_id, "P11"),
				">"					: (adiciona_id, "P13"),
				"<"					: (adiciona_id, "P13"),
				";"					: (escreve_lst_entrada, "P10"),
				"instrucao"			: (adiciona_id, "P12")
			},
			"P1":{
				"controle"			: (escreve_lst_entrada, "P1")
			},
			"P2":{
				"n-terminal"		: (adiciona_id, "P1")
			},
			"P3":{
				"/"					: (adiciona_id, "P4"),
				"="					: (adiciona_id, "P5"),
				"@"					: (adiciona_id, "P6"),
				"#"					: (adiciona_id, "P7"),
				"'"					: (adiciona_id, "P8")
			},
			"P4":{
				"terminal"			: (gera_valor, "P9")
			},
			"P5":{
				"terminal"			: (gera_valor, "P9")
			},
			"P6":{
				"terminal"			: (gera_valor, "P9")
			},
			"P7":{
				"terminal"			: (gera_valor, "P9")
			},
			"P8":{
				"n-terminal"		: (gera_valor, "P9")
			},
			"P9":{
				";"					: (gera_codigo_de_valor, "P10"),
				"controle"			: (gera_codigo_de_valor, "P0")
			},
			"P10":{
				"controle"			: (escreve_lst_entrada, "P0"),
				"terminal"			: (escreve_lst_entrada, "P10"),
				"n-terminal"		: (escreve_lst_entrada, "P10"),
				"#"					: (escreve_lst_entrada, "P10"),
				"@"					: (escreve_lst_entrada, "P10"),
				"&"					: (escreve_lst_entrada, "P10"),
				";"					: (escreve_lst_entrada, "P10"),
				"/"					: (escreve_lst_entrada, "P10"),
				"="					: (escreve_lst_entrada, "P10"),
				"'"					: (escreve_lst_entrada, "P10"),
				">"					: (escreve_lst_entrada, "P10"),
				"<"					: (escreve_lst_entrada, "P10"),
				"instrucao"			: (escreve_lst_entrada, "P10")
			},
			"P11":{
				"instrucao"			: (adiciona_id, "P12")
			},
			"P12":{
				"/"					: (adiciona_id, "P4"),
				"="					: (adiciona_id, "P5"),
				"@"					: (adiciona_id, "P6"),
				"#"					: (adiciona_id, "P7"),
				"'"					: (adiciona_id, "P8"),
				"n-terminal"		: (adiciona_id, "P14")
			},
			"P13":{
				"n-terminal"		: (adiciona_id, "P14")
			},
			"P14":{
				";"					: (gera_codigo_de_rotulo, "P10"),
				"controle"			: (gera_codigo_de_rotulo, "P0")
			}
}

transicoes_semantico=transicoes_semantico_3

#Máquina de estado que gera todo o código compilado
semantico_3=MotorDeEventos(backup, {"terminal":semantico_terminal,
								    "n-terminal":semantico_nterminal,
								    "reservada":semantico_reservada,
								    "instrucao":semantico_instrucao,
								    "controle":semantico_controle,
								    "eof":semantico_eof})

palavra=semantico_3.roda_um_evento((0, ESTADO_INICIAL, []))

if SEMANTICO<3:
	sys.exit()

if VERBOSIDADE>1:
	print("\nIniciando análise semântica 3\n-----------------------------")

while semantico_3.fila_de_eventos!=None:
	palavra=semantico_3.roda_um_evento(palavra)

if VERBOSIDADE>0:
	print(f"{VERDE}O código final foi gerado.{BRANCO}")

if not GERAR:
	sys.exit()

arquivo_saida_mvn=open(CODIGO_OUT+".mvn", "w")
arquivo_saida_mvn.write(codigo_mvn)
arquivo_saida_mvn.close()

arquivo_saida_lst=open(CODIGO_OUT+".lst", "w")
arquivo_saida_lst.write(codigo_lst)
arquivo_saida_lst.close()

if VERBOSIDADE>0:
	print(f"{VERDE}Tudo pronto.\nbIlo'meH qatlho'!!!{BRANCO}")