from Medu import MercadoEdu
import pandas as pd

if __name__ == "__main__":
	# Array para iterar no map.
	it = ['Administração', 'Ciências Contábeis', 'Enfermagem' ]
	
	# Uma alternativa escalável

	k = [*map(MercadoEdu, it)]
	df = pd.concat([a.dados() for a in k])
	df.to_csv('database.csv', index = False)
	print("Arquivo gerado!")
