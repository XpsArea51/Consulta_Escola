import pandas as pd
import re

# Função para limpar os nomes das IES
def limpar_nome(nome):
    nome = nome.upper()  # Converter para maiúsculo
    nome = re.sub(r'[^\w\s]', '', nome)  # Remover caracteres especiais, mantendo espaços
    return nome

# Carregar os dados das duas planilhas
df1 = pd.read_csv('data/PDA_Lista_Instituicoes_Ensino_Superior_do_Brasil_EMEC_modificado.csv', delimiter=';')
df2 = pd.read_csv('base_censo.csv', delimiter=';')

# Aplicar a função de limpeza aos nomes das IES
df1['NOME_DA_IES'] = df1['NOME_DA_IES'].apply(limpar_nome)

# Renomear e selecionar as colunas necessárias de df1
df1 = df1[['CODIGO_DA_IES', 'NOME_DA_IES', 'MUNICIPIO', 'UF']]
df1.columns = ['Código INEP', 'Escola', 'Município', 'UF']

# Concatenar df2 com as linhas selecionadas de df1
df_final = pd.concat([df2, df1], ignore_index=True)

# Salvar o dataframe final em um novo arquivo CSV
df_final.to_csv('novo_censo.csv', index=False, sep=';')

