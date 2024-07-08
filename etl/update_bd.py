import os
import asyncio
import pandas as pd

from prisma import Prisma

db = Prisma()

async def raw_sql_insert(df: pd.DataFrame, table_name: str):
    """
    Inserts a pandas DataFrame into a SQL table using raw SQL query with Prisma.

    Args:
        df (pd.DataFrame): The DataFrame to be inserted.
        table_name (str): The name of the SQL table.
    """
    # Converte o DataFrame em uma lista de dicionários
    records = df.to_dict(orient='records')

    # Constrói a consulta SQL de inserção em massa
    # Esta é uma abordagem genérica e pode precisar de ajustes para casos específicos
    columns = ', '.join(records[0].keys())
    values = ', '.join(['(' + ', '.join([f"'{v}'" for v in record.values()]) + ')' for record in records])
    sql_query = f"INSERT INTO {table_name} ({columns}) VALUES {values};"

    # Executa a consulta SQL bruta
    await db.execute_raw(sql_query)
    
async def main():
    """
    This function updates the database with data from CSV files.

    It connects to the database, reads data from CSV files, inserts the data into the corresponding tables,
    and then disconnects from the database.
    """
    await db.connect()

    models_files = {
        'dtempo': os.path.join(os.getcwd(), 'dados/df_dtempo.csv'),
        'dlocalizacao': os.path.join(os.getcwd(), 'dados/df_dlocalizacao.csv'),
        'destacao': os.path.join(os.getcwd(), 'dados/df_destacao.csv'),
        'fqualidadear': os.path.join(os.getcwd(), 'dados/df_fqualidadear.csv'),
    }

    for model, file_name in models_files.items():
        df = pd.read_csv(file_name)
        records = df.to_dict(orient='records')

        print(f'Inserindo {len(records)} registros na tabela {model}')
        await raw_sql_insert(df, model)

    await db.disconnect()

# Execute a função principal
asyncio.run(main())
