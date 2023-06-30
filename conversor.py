import pandas as pd

# Carregar o arquivo CSV em um dataframe
df = pd.read_csv('data/Análise - Tabela da lista das escolas - Detalhado.csv', delimiter=';')

# Selecionar apenas as colunas desejadas
df = df[['Escola', 'Código INEP', 'UF', 'Município', 'Endereço', 'Latitude', 'Longitude']]

# Salvar o dataframe modificado em um novo arquivo CSV
df.to_csv('base_censo.csv', index=False, sep=';')
