import pandas as pd
import os

def create_df_dtempo(df):
    df_dtempo = pd.DataFrame()
    df_aux = df_dtempo.copy()
    
    df_aux['timestamp'] = pd.to_datetime(df['data'], format='%Y/%m/%d %H:%M:%S%z')

    # Pegar apenas chaves únicas
    df_dtempo['timestamp'] = df_aux['timestamp'].unique()

    df_dtempo['ano'] = df_dtempo['timestamp'].dt.year
    df_dtempo['mes'] = df_dtempo['timestamp'].dt.month
    df_dtempo['dia'] = df_dtempo['timestamp'].dt.day
    df_dtempo['hora'] = df_dtempo['timestamp'].dt.hour

    df_dtempo['tempo_key'] = df_dtempo.index + 1

    df_dtempo = df_dtempo[['tempo_key', 'ano', 'mes', 'dia', 'hora', 'timestamp']]

    df_dtempo_export = df_dtempo[['tempo_key', 'ano', 'mes', 'dia', 'hora']]

    df_dtempo_export.to_csv(os.path.join(os.getcwd(), 'dados/df_dtempo.csv'), index=False)

    return df_dtempo

def create_df_dlocalizacao(df):
    df_dlocalizacao = pd.DataFrame()
    df_aux = df_dlocalizacao.copy()

    df_aux = df[~df.duplicated(subset=['lat', 'lon'])]

    df_dlocalizacao['latitude'] = df_aux['lat']
    df_dlocalizacao['longitude'] = df_aux['lon']

    df_dlocalizacao = df_dlocalizacao.reset_index(drop=True)
    df_dlocalizacao['localizacao_key'] = df_dlocalizacao.index + 1

    df_dlocalizacao = df_dlocalizacao[['localizacao_key', 'latitude', 'longitude']]

    df_dlocalizacao.to_csv(os.path.join(os.getcwd(), 'dados/df_dlocalizacao.csv'), index=False)

    return df_dlocalizacao

def create_df_destacao(df):
    df_destacao = pd.DataFrame()
    df_aux = df_destacao.copy()

    df_aux = df[~df.duplicated(subset=['codnum', 'estação'])]

    df_destacao['station_id'] = df_aux['codnum']
    df_destacao['station_name'] = df_aux['estação']

    df_destacao = df_destacao.reset_index(drop=True)
    df_destacao['estacao_key'] = df_destacao.index + 1

    df_destacao = df_destacao[['estacao_key', 'station_id', 'station_name']]

    df_destacao.to_csv(os.path.join(os.getcwd(), 'dados/df_destacao.csv'), index=False)

    return df_destacao

def create_df_fqualidadear(df, df_dtempo, df_dlocalizacao, df_destacao):
    df_fqualidadear = pd.DataFrame()
    
    df_aux = df.copy()
    df_aux['timestamp'] = pd.to_datetime(df['data'], format='%Y/%m/%d %H:%M:%S%z')
    
    df_tempo_key = pd.merge(df_aux, df_dtempo, left_on=['timestamp'], right_on=['timestamp'], how='inner')
    df_localizacao_key = pd.merge(df_tempo_key, df_dlocalizacao, left_on=['lat', 'lon'], right_on=['latitude', 'longitude'], how='inner')
    df_estacao_key = pd.merge(df_localizacao_key, df_destacao, left_on=['codnum', 'estação'], right_on=['station_id', 'station_name'], how='inner')

    df_fqualidadear = df_estacao_key[['tempo_key', 'estacao_key', 'localizacao_key', 'chuva', 'pres', 'rs', 'temp',
       'ur', 'dir_vento', 'vel_vento', 'so2', 'no2', 'hcnm', 'hct', 'ch4', 'co', 'no', 'nox', 'o3', 'pm10', 'pm2_5']]
    
    df_fqualidadear.to_csv(os.path.join(os.getcwd(), 'dados/df_fqualidadear.csv'), index=True, index_label='id')

    return df_fqualidadear

df = pd.read_csv(os.path.join(os.getcwd(), 'dados/dados_iqarj.csv'))

# Removendo colunas Sirgas
df = df.drop(columns=['x_utm_sirgas2000', 'y_utm_sirgas2000'])

df_dtempo = create_df_dtempo(df)
df_dlocalizacao = create_df_dlocalizacao(df)
df_destacao = create_df_destacao(df)
df_fqualidadear = create_df_fqualidadear(df, df_dtempo, df_dlocalizacao, df_destacao)

print(df_fqualidadear)