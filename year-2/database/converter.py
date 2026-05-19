"""
Importação de Dados Excel para um banco de dados SQLite

Pré-requisitos: Instalar as bibliotecas pandas e sqlalchemy (executar no terminal o comando pip install pandas sqlalchemy)
Configuração: Certificar que o arquivo Excel está no mesmo	diretório do script Python ou fornecer o caminho correto e
alterar as variáveis no script Python conforme necessário
Execução: Executar o script Python, no terminal (python script.py)
"""

import pandas as pd
from sqlalchemy import create_engine

# Step 1: Load Excel file into a pandas DataFrame
excel_file = 'morbilidade-e-mortalidade-hospitalar.xlsx'  # Replace with your file name
sheet_name = 'Sheet'                                      # Replace with your sheet name, or use None to load all sheets
df = pd.read_excel(excel_file, sheet_name=sheet_name)

# Step 2: Connect to SQLite database (or create one if it doesn't exist)
database_name = 'data.db'                                 # Replace with your desired database name
engine = create_engine(f'sqlite:///{database_name}')

# Step 3: Write the DataFrame to the database
table_name = 'data_table'                                 # Replace with your desired table name
df.to_sql(table_name, con=engine, if_exists='replace', index=False)

print(f"Data has been written to the {table_name} table in the {database_name} database.")