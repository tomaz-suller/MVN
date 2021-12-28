'''
Classe para simular um motor de eventos do compilador
'''

from eventos import Evento

class MotorDeEventos:
	def __init__(self, fila_de_eventos:Evento, rotinas:dict):
		self.fila_de_eventos=fila_de_eventos
		self.rotinas=rotinas

	def insere_na_fila(self, evento:Evento):
		nova_chave=evento.chave_ordenacao
		atual_evento=self.fila_de_eventos
		while atual_evento.proximo!=None and nova_chave>atual_evento.proximo.chave_ordenacao:
			atual_evento=atual_evento.proximo
		if atual_evento.proximo==None:
			atual_evento.proximo=evento
			return
		if nova_chave==atual_evento.proximo.chave_ordenacao:
			raise ValueError("Dois eventos com mesma chave.")
		evento.proximo=atual_evento.proximo
		atual_evento.proximo=evento

	def tira_da_fila(self):
		primeiro=self.fila_de_eventos
		self.fila_de_eventos=self.fila_de_eventos.proximo
		return primeiro

	def roda_um_evento(self, extra_params:tuple=()):
		evento=self.tira_da_fila()
		rotina=self.rotinas[evento.tipo]
		return rotina(evento.parametros, extra_params)

	def primeira_chave(self):
		return self.fila_de_eventos.chave_ordenacao

	def ultima_chave(self):
		atual_evento=self.fila_de_eventos
		while atual_evento.proximo!=None:
			atual_evento=atual_evento.proximo
		return atual_evento.chave_ordenacao