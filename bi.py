import streamlit as st
import pandas as pd
import pydeck as pdk
import numpy as np

st.set_page_config(layout="wide")

# Carregar os dados
df_qualidade_ar = pd.read_csv('dados/df_fqualidadear.csv')
df_tempo = pd.read_csv('dados/df_dtempo.csv')
df_estacao = pd.read_csv('dados/df_destacao.csv')
df_localizacao = pd.read_csv('dados/df_dlocalizacao.csv')

# Convertendo colunas de datas para datetime
df_tempo['timestamp'] = pd.to_datetime(df_tempo['timestamp'])

# Unir os dataframes
df = df_qualidade_ar.merge(df_tempo, how='left', left_on='tempo_key', right_on='tempo_key')
df = df.merge(df_estacao, how='left', left_on='estacao_key', right_on='estacao_key')
df = df.merge(df_localizacao, how='left', left_on='localizacao_key', right_on='localizacao_key')

# Renomear colunas para facilitar a leitura
df.rename(columns={'timestamp': 'data', 'station_name': 'Estação', 'latitude': 'Latitude', 'longitude': 'Longitude'}, inplace=True)

st.title('Análise da Qualidade do Ar')

# Funções de formatação
def human_format(num):
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return ('%.2f%s' % (num, ['', 'K', 'M', 'G', 'T', 'P'][magnitude])).replace('.00', '')

# Filtros
selectbox_estacao = st.sidebar.multiselect('Estações', df['Estação'].unique(), default=[df['Estação'].unique()[0]])
df_filtered = df[df['Estação'].isin(selectbox_estacao)]

# Seleção da granularidade do tempo
granularity = st.sidebar.selectbox('Granularidade do Tempo', ['Ano', 'Mês', 'Dia', 'Hora'], index=2)

if granularity == 'Ano':
    df_filtered['tempo'] = df_filtered['data'].dt.year
elif granularity == 'Mês':
    df_filtered['tempo'] = df_filtered['data'].dt.to_period('M')
elif granularity == 'Dia':
    df_filtered['tempo'] = df_filtered['data'].dt.date
elif granularity == 'Hora':
    df_filtered['tempo'] = df_filtered['data'].dt.hour

# Filtro de intervalo de datas
min_date = df_filtered['data'].min().date()
max_date = df_filtered['data'].max().date()
start_date = max_date.replace(year=max_date.year - 1) if max_date.year > min_date.year else min_date
end_date = max_date
try:
    start_date, end_date = st.sidebar.date_input('Selecionar Período', [start_date, end_date], min_value=min_date, max_value=max_date)
except Exception:
    st.warning('Selecione um intervalo adequado.')

df_filtered = df_filtered[(df_filtered['data'].dt.date >= start_date) & (df_filtered['data'].dt.date <= end_date)]

# Seleção de múltiplos atributos
poluentes = ['chuva', 'pres', 'rs', 'temp', 'ur', 'dir_vento', 'vel_vento', 'so2', 'no2', 'hcnm', 'hct', 'ch4', 'co', 'no', 'nox', 'o3', 'pm10', 'pm2_5']
selectbox_poluentes = st.sidebar.multiselect('Indicadores', poluentes, default=poluentes[:3])

# Ordenação
selectbox_orderby = st.sidebar.selectbox(
    "Order By", ['Data'] + [f'{poluente} ↓' for poluente in selectbox_poluentes] + [f'{poluente} ↑' for poluente in selectbox_poluentes]
)
orderby_column = 'data'
orderby_asc = True

if selectbox_orderby == 'Data':
    orderby_column = 'data'
    orderby_asc = True
elif '↓' in selectbox_orderby:
    orderby_column = selectbox_orderby.replace(' ↓', '')
    orderby_asc = False
elif '↑' in selectbox_orderby:
    orderby_column = selectbox_orderby.replace(' ↑', '')
    orderby_asc = True

df_filtered.sort_values(by=[orderby_column], inplace=True, ascending=orderby_asc)

# Scorecards
col1, col2, col3, col4 = st.columns(4)
col1.metric("Mediçōes", df_filtered[selectbox_poluentes].count().sum())
col2.metric("Concentração Total", human_format(df_filtered[selectbox_poluentes].sum().sum()))

# Identificar o período com a média mais alta
if granularity == 'Ano':
    max_period = df_filtered.groupby(df_filtered['data'].dt.year)[selectbox_poluentes].mean().mean(axis=1).idxmax()
    max_period_label = f"Ano: {max_period}"
elif granularity == 'Mês':
    max_period = df_filtered.groupby(df_filtered['data'].dt.to_period('M'))[selectbox_poluentes].mean().mean(axis=1).idxmax()
    max_period_label = f"Mês: {max_period}"
elif granularity == 'Dia':
    max_period = df_filtered.groupby(df_filtered['data'].dt.date)[selectbox_poluentes].mean().mean(axis=1).idxmax()
    max_period_label = f"Dia: {max_period}"
elif granularity == 'Hora':
    max_period = df_filtered.groupby(df_filtered['data'].dt.hour)[selectbox_poluentes].mean().mean(axis=1).idxmax()
    max_period_label = f"Hora: {max_period}"

col3.metric("Período com Média mais Alta", max_period_label)

# Identificar a estação com a média mais alta
max_station = df_filtered.groupby('Estação')[selectbox_poluentes].mean().mean(axis=1).idxmax()
col4.metric("Estação com Média mais Alta", max_station)

# Gráfico de barras
st.subheader('Gráfico de Média do(s) Indicador(es)')
if granularity == 'Ano':
    df_grouped = df_filtered.groupby(df_filtered['data'].dt.year)[selectbox_poluentes].mean()
    df_grouped.index.name = 'Ano'
elif granularity == 'Mês':
    df_grouped = df_filtered.groupby(df_filtered['data'].dt.to_period('M'))[selectbox_poluentes].mean()
    df_grouped.index.name = 'Mês'
elif granularity == 'Dia':
    df_grouped = df_filtered.groupby(df_filtered['data'].dt.date)[selectbox_poluentes].mean()
    df_grouped.index.name = 'Dia'
elif granularity == 'Hora':
    df_grouped = df_filtered.groupby(df_filtered['data'].dt.hour)[selectbox_poluentes].mean()
    df_grouped.index.name = 'Hora'
st.bar_chart(df_grouped)

# Gráfico geográfico
st.subheader('Mapa da(s) Média(s) do(s) Indicador(es) por Estação')
df_station_means = df_filtered.groupby(['Estação', 'Latitude', 'Longitude'])[selectbox_poluentes].mean().reset_index()

# Criar string de indicadores para o tooltip
df_station_means['tooltip'] = df_station_means.apply(
    lambda row: '\n'.join([f"{poluente}: {row[poluente]:.2f}" if not pd.isna(row[poluente]) else f"{poluente}: --" for poluente in selectbox_poluentes]),
    axis=1
)

layer = pdk.Layer(
    'ScatterplotLayer',
    df_station_means,
    get_position=['Longitude', 'Latitude'],
    get_radius=500,
    get_fill_color=[255, 255, 0, 150],  # Cor amarela
    pickable=True,
    auto_highlight=True,
    get_tooltip='tooltip'
)
view_state = pdk.ViewState(
    latitude=df['Latitude'].mean(),
    longitude=df['Longitude'].mean(),
    zoom=10
)
r = pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip={"text": "{Estação}\n{tooltip}"})
st.pydeck_chart(r)

# Visualização dos dados
with st.expander("Tabela"):
    st.dataframe(df_filtered[['data', 'Estação', 'Latitude', 'Longitude'] + selectbox_poluentes])
