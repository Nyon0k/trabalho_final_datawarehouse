import pandas as pd
import os

def create_df_dtempo(df, df_dtempo_existing):
    """
    Create a dataframe for the dimension table 'df_dtempo' based on the given input dataframe and existing 'df_dtempo' dataframe.

    Args:
        df (pandas.DataFrame): Input dataframe containing the data.
        df_dtempo_existing (pandas.DataFrame): Existing 'df_dtempo' dataframe.

    Returns:
        pandas.DataFrame: The updated 'df_dtempo' dataframe.

    """
    df_aux = pd.DataFrame()
    df_aux['timestamp'] = pd.to_datetime(df['data'])

    # Pegar apenas chaves únicas
    df_dtempo_new = pd.DataFrame({'timestamp': df_aux['timestamp'].unique()})

    df_dtempo_new['ano'] = df_dtempo_new['timestamp'].dt.year
    df_dtempo_new['mes'] = df_dtempo_new['timestamp'].dt.month
    df_dtempo_new['dia'] = df_dtempo_new['timestamp'].dt.day
    df_dtempo_new['hora'] = df_dtempo_new['timestamp'].dt.hour

    if not df_dtempo_existing.empty:
        df_dtempo_existing['timestamp'] = pd.to_datetime(df_dtempo_existing['timestamp'])
        df_dtempo_new = df_dtempo_new[~df_dtempo_new['timestamp'].isin(df_dtempo_existing['timestamp'])]
        df_dtempo_new['tempo_key'] = df_dtempo_existing['tempo_key'].max() + 1 + df_dtempo_new.index
        df_dtempo_export = pd.concat([df_dtempo_existing, df_dtempo_new])
    else:
        df_dtempo_new['tempo_key'] = df_dtempo_new.index + 1
        df_dtempo_export = df_dtempo_new

    # df_dtempo_export[['tempo_key', 'ano', 'mes', 'dia', 'hora']].to_csv(os.path.join(os.getcwd(), 'dados/df_dtempo.csv'), index=False)
    df_dtempo_export.to_csv(os.path.join(os.getcwd(), 'dados/df_dtempo.csv'), index=False)

    return df_dtempo_export

def create_df_dlocalizacao(df, df_dlocalizacao_existing):
    df_aux = df[~df.duplicated(subset=['lat', 'lon'])]

    df_dlocalizacao_new = pd.DataFrame({
        'latitude': df_aux['lat'],
        'longitude': df_aux['lon']
    })

    df_dlocalizacao_new = df_dlocalizacao_new.reset_index(drop=True)
    if not df_dlocalizacao_existing.empty:
        df_dlocalizacao_new = df_dlocalizacao_new[~df_dlocalizacao_new.apply(lambda x: (x['latitude'], x['longitude']), axis=1).isin(
            df_dlocalizacao_existing.apply(lambda x: (x['latitude'], x['longitude']), axis=1))]
        df_dlocalizacao_new['localizacao_key'] = df_dlocalizacao_existing['localizacao_key'].max() + 1 + df_dlocalizacao_new.index
        df_dlocalizacao_export = pd.concat([df_dlocalizacao_existing, df_dlocalizacao_new])
    else:
        df_dlocalizacao_new['localizacao_key'] = df_dlocalizacao_new.index + 1
        df_dlocalizacao_export = df_dlocalizacao_new

    df_dlocalizacao_export.to_csv(os.path.join(os.getcwd(), 'dados/df_dlocalizacao.csv'), index=False)

    return df_dlocalizacao_export

def create_df_destacao(df, df_destacao_existing):
    df_aux = df[~df.duplicated(subset=['codnum', 'estação'])]

    df_destacao_new = pd.DataFrame({
        'station_id': df_aux['codnum'],
        'station_name': df_aux['estação']
    })

    df_destacao_new = df_destacao_new.reset_index(drop=True)
    if not df_destacao_existing.empty:
        df_destacao_new = df_destacao_new[~df_destacao_new.apply(lambda x: (x['station_id'], x['station_name']), axis=1).isin(
            df_destacao_existing.apply(lambda x: (x['station_id'], x['station_name']), axis=1))]
        df_destacao_new['estacao_key'] = df_destacao_existing['estacao_key'].max() + 1 + df_destacao_new.index
        df_destacao_export = pd.concat([df_destacao_existing, df_destacao_new])
    else:
        df_destacao_new['estacao_key'] = df_destacao_new.index + 1
        df_destacao_export = df_destacao_new

    df_destacao_export.to_csv(os.path.join(os.getcwd(), 'dados/df_destacao.csv'), index=False)

    return df_destacao_export

def create_df_fqualidadear(df, df_dtempo, df_dlocalizacao, df_destacao, df_fqualidadear_existing):
    """
    Create a new DataFrame for fqualidadear data by merging and processing the given input DataFrames.

    Args:
        df (pandas.DataFrame): The main DataFrame containing the data.
        df_dtempo (pandas.DataFrame): The DataFrame containing time-related data.
        df_dlocalizacao (pandas.DataFrame): The DataFrame containing location-related data.
        df_destacao (pandas.DataFrame): The DataFrame containing station-related data.
        df_fqualidadear_existing (pandas.DataFrame): The existing DataFrame for fqualidadear data.

    Returns:
        pandas.DataFrame: The resulting DataFrame for fqualidadear data.

    """
    df_aux = df.copy()
    df_aux['timestamp'] = pd.to_datetime(df['data'])

    df_dtempo['timestamp'] = pd.to_datetime(df_dtempo['timestamp'])
    df_tempo_key = pd.merge(df_aux, df_dtempo, left_on=['timestamp'], right_on=['timestamp'], how='inner')

    df_localizacao_key = pd.merge(df_tempo_key, df_dlocalizacao, left_on=['lat', 'lon'], right_on=['latitude', 'longitude'], how='inner')
    df_estacao_key = pd.merge(df_localizacao_key, df_destacao, left_on=['codnum', 'estação'], right_on=['station_id', 'station_name'], how='inner')

    df_fqualidadear_new = df_estacao_key[['tempo_key', 'estacao_key', 'localizacao_key', 'chuva', 'pres', 'rs', 'temp',
       'ur', 'dir_vento', 'vel_vento', 'so2', 'no2', 'hcnm', 'hct', 'ch4', 'co', 'no', 'nox', 'o3', 'pm10', 'pm2_5']]

    if not df_fqualidadear_existing.empty:
        df_fqualidadear_new = df_fqualidadear_new[~df_fqualidadear_new.apply(tuple, axis=1).isin(df_fqualidadear_existing.apply(tuple, axis=1))]
        df_fqualidadear_export = pd.concat([df_fqualidadear_existing, df_fqualidadear_new])
    else:
        df_fqualidadear_export = df_fqualidadear_new

    # Remove duplicates based on specified columns
    df_fqualidadear_export = df_fqualidadear_export.drop_duplicates(subset=['tempo_key', 'estacao_key', 'localizacao_key', 'chuva', 'pres', 'rs', 'temp', 'ur', 'dir_vento', 'vel_vento', 'so2', 'no2', 'hcnm', 'hct', 'ch4', 'co', 'no', 'nox', 'o3', 'pm10', 'pm2_5'])

    # Remove 'id' columns if they exist
    df_fqualidadear_export = df_fqualidadear_export.loc[:, ~df_fqualidadear_export.columns.str.startswith('id')]

    # Add a new 'id' column
    df_fqualidadear_export.reset_index(drop=True, inplace=True)
    df_fqualidadear_export.index.name = 'id'
    
    df_fqualidadear_export.to_csv(os.path.join(os.getcwd(), 'dados/df_fqualidadear.csv'), index=True)

    return df_fqualidadear_export

def etl_function(df):
    """
    Performs the ETL (Extract, Transform, Load) process on the given DataFrame.

    Parameters:
    - df (pandas.DataFrame): The input DataFrame containing the data to be processed.

    This function drops unnecessary columns from the input DataFrame and creates or updates
    several other DataFrames based on the extracted data. The resulting DataFrames are then
    printed to the console.
    """
    df = df.drop(columns=['x_utm_sirgas2000', 'y_utm_sirgas2000'])

    # Carregar os DataFrames existentes, se existirem
    df_dtempo_existing = pd.read_csv(os.path.join(os.getcwd(), 'dados/df_dtempo.csv')) if os.path.exists(os.path.join(os.getcwd(), 'dados/df_dtempo.csv')) else pd.DataFrame(columns=['tempo_key', 'ano', 'mes', 'dia', 'hora', 'timestamp'])
    df_dlocalizacao_existing = pd.read_csv(os.path.join(os.getcwd(), 'dados/df_dlocalizacao.csv')) if os.path.exists(os.path.join(os.getcwd(), 'dados/df_dlocalizacao.csv')) else pd.DataFrame(columns=['localizacao_key', 'latitude', 'longitude'])
    df_destacao_existing = pd.read_csv(os.path.join(os.getcwd(), 'dados/df_destacao.csv')) if os.path.exists(os.path.join(os.getcwd(), 'dados/df_destacao.csv')) else pd.DataFrame(columns=['estacao_key', 'station_id', 'station_name'])
    df_fqualidadear_existing = pd.read_csv(os.path.join(os.getcwd(), 'dados/df_fqualidadear.csv')) if os.path.exists(os.path.join(os.getcwd(), 'dados/df_fqualidadear.csv')) else pd.DataFrame(columns=['tempo_key', 'estacao_key', 'localizacao_key', 'chuva', 'pres', 'rs', 'temp', 'ur', 'dir_vento', 'vel_vento', 'so2', 'no2', 'hcnm', 'hct', 'ch4', 'co', 'no', 'nox', 'o3', 'pm10', 'pm2_5'])

    df_dtempo = create_df_dtempo(df, df_dtempo_existing)
    df_dlocalizacao = create_df_dlocalizacao(df, df_dlocalizacao_existing)
    df_destacao = create_df_destacao(df, df_destacao_existing)
    df_fqualidadear = create_df_fqualidadear(df, df_dtempo, df_dlocalizacao, df_destacao, df_fqualidadear_existing)
    
    print(df_fqualidadear)

def predata_validator(file_path, history_path, etl_function):
    """
    Validates the input data file and performs the ETL process if necessary.

    Args:
        file_path (str): The path to the input data file.
        history_path (str): The path to the history file.
        etl_function (function): The function to be used for the ETL process.

    Raises:
        FileNotFoundError: If the input data file does not exist.
    """
    # Verifica se os arquivos existem
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"O arquivo {file_path} não foi encontrado.")
    
    current_df = pd.read_csv(file_path)
    current_df['data'] = pd.to_datetime(current_df['data'])
    
    if os.path.exists(history_path):
        history_df = pd.read_csv(history_path)
        history_df['data'] = pd.to_datetime(history_df['data'])
        
        # Verifica se os DataFrames são iguais
        if current_df.equals(history_df):
            print("Nenhuma diferença encontrada. Processo de ETL não necessário.")
            return
        
        # Encontra as diferenças
        differences = pd.concat([current_df, history_df]).drop_duplicates(keep=False)

        if differences.empty:
            print("Nenhuma diferença encontrada. Processo de ETL não necessário.")
            return
        
        # Processa as diferenças usando a função ETL fornecida
        etl_function(differences)
        
        # Atualiza o arquivo de histórico
        history_df = pd.concat([history_df, differences]).drop_duplicates()
        history_df.to_csv(history_path, index=False)
    else:
        print("Arquivo de histórico não encontrado. Processando todo o arquivo atual.")
        etl_function(current_df)
        current_df.to_csv(history_path, index=False)

file_path = os.path.join(os.getcwd(), 'dados/dados_iqarj.csv')
history_path = os.path.join(os.getcwd(), 'dados/dados_iqarj_historicos.csv')

predata_validator(file_path, history_path, etl_function)
