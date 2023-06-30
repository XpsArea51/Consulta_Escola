import pandas as pd
import numpy as np

# Carregar os dados
df = pd.read_csv('data/PDA_Lista_Instituicoes_Ensino_Superior_do_Brasil_EMEC (1).csv', delimiter=';')

# Aplicar a função a cada linha
df['NOME_DA_IES'] = df.apply(lambda row: row['NOME_DA_IES'] if pd.isnull(row['SIGLA']) else f"{row['NOME_DA_IES']} - {row['SIGLA']}", axis=1)

# Salvar o DataFrame modificado
df.to_csv('data/PDA_Lista_Instituicoes_Ensino_Superior_do_Brasil_EMEC_modificado.csv', sep=';', index=False)
