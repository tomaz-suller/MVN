'''
Classe de eventos para alimentar um motor de eventos do compilador
'''

class Evento:
	def __init__(self, chave_ordenacao:int, tipo:str, parametros:tuple, proximo=None):
		self.chave_ordenacao=chave_ordenacao
		self.tipo=tipo
		self.parametros=parametros
		self.proximo=proximo