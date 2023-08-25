from Medu import MercadoEdu
import pandas as pd

if __name__ == "__main__":
	adm = MercadoEdu('Administração').dados() 
	cc = MercadoEdu('Ciências Contábeis').dados()
	enf = MercadoEdu('Enfermagem').dados()

	df = pd.concat([adm, cc, enf], axis = 0)
	df.to_csv('database.csv', index = False)
	print("Arvquivo gerado!")
