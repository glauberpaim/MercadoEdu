import requests
import json
import pandas as pd
from bs4 import BeautifulSoup

class MercadoEdu:
	def __init__(self, nome):
		self.data = None
		self.headers = {}
		self.nome = nome
		self.cache_Modalidades = None
		self.export = []
		self.form = self.verificar()
	
	# Centraliza todas as requisiçãos (requests) e faz o 
	#tratamento de erros antes de qualquer conexão seja feita
	
	def conectar(self, url):
		try:
			r = requests.get(url, headers = self.headers)
			if(r.status_code == 200):
				return r
			else:
				print(f'Erro na conexão {r.status_code}')
		except requests.exceptions.RequestException as e:
			print(f'Houve algum erro na requisição {e}')

	# Faz a busca na api de todas modalidades para o curso determinado
	def modalidades(self):
		if self.cache_Modalidades is not None:
			return self.cache_Modalidades
		codigo = self.codigoCurso(self.nome)
		query = f'/estados-por-modalidades?idsMarca=1&codigoTipoCurso=11&codigoCurso={codigo}&modalidades=PRESENCIAL,TOTAL%20EAD,SEMIPRESENCIAL,AO%20VIVO'
		r = self.api(query)
		dados = json.loads(r.text)
		self.cache_Modalidades = dados
		return dados		

	# Chamada para a api url base e a query
	def api(self, query):
		endpoint = f'https://api.portal.estacio.br/ofertas/api/v1/ofertas'
		r = self.conectar(f'{endpoint}{query}')
		return r
	
	# Faz o scrap para buscar os códigos dos cursos 
	def verificar(self):
		if self.data is not None:
			return self.data
		
		url = f'https://aprenda.estacio.br/selecao?formacao=grad'
		self.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
		form = self.conectar(url)
		soup = BeautifulSoup(form.text, 'html.parser')
		
		try:
			item = soup.find('script', {'id': '__NEXT_DATA__'})
			js = json.loads(item.text)
			curso_data = [{'codigo': a.get('code'), 'nome' : a.get('name')} for a in js['props'].get('pageProps').get('courses')]
			self.data = curso_data
			return self.data
		except Exception as e:
			print("Houve algum erro no Elemento soup find {e}")
	# Procura um curso por nome e retorna o código do curso
	def codigoCurso(self, nome):
		item = [a.get('codigo') for a in self.data if a.get('nome') == nome]
		return next(iter(item))

	#  Faz a extração dos dados necessários 
	# (Nome do curso, modalidade, Turno, Cidade, Bairro/local, Valor normal e valor com desconto)
	def extrair(self):
		codigo = self.codigoCurso(self.nome)
		for a in [*self.modalidades()['map'].keys()]:
			query = f'?idsMarca=1&uf=RS&codigoTipoCurso=11&codigoCurso={codigo}&modalidade='
			r = self.api(f'{query}{a}')
			data = json.loads(r.text)
			f = [self.export.append(
				{'NOME_DO_CURSO': self.nome, 'MODALIDADE' : a.get('modalidade'),
				'TURNO' : a.get('nomeTurno'), 'CIDADE' : a['endereco'].get('municipio'),  
				'LOCAL' : a['endereco'].get('bairro'), 'PRECO' : a.get('valorDe'), 
					'PRECO_COM_DESCONTO': a.get('valorPara')})
					 for a in data]
		return self.export
	# Retorna o DataFrame a partir da extração
	def dados(self):
		#self.modalidades()
		df = pd.DataFrame(self.extrair())
		return df