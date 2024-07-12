import streamlit as st
import pandas as pd
import pydeck as pdk
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px

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
df_filtered = df[df['Estação'].isin(selectbox_estacao)].copy()

# Seleção da granularidade do tempo
granularity = st.sidebar.selectbox('Granularidade do Tempo', ['Ano', 'Mês', 'Dia', 'Hora'], index=2)

if granularity == 'Ano':
    df_filtered.loc[:, 'tempo'] = df_filtered['data'].dt.year
    order = None  # Não precisamos definir ordem específica para anos
elif granularity == 'Mês':
    df_filtered.loc[:, 'tempo'] = df_filtered['data'].dt.to_period('M').astype(str)
    order = [f'{y}-{m:02}' for y in range(df_filtered['data'].dt.year.min(), df_filtered['data'].dt.year.max() + 1) for m in range(1, 13)]
elif granularity == 'Dia':
    df_filtered.loc[:, 'tempo'] = df_filtered['data'].dt.date
    order = None  # A ordem será mantida naturalmente
elif granularity == 'Hora':
    df_filtered.loc[:, 'tempo'] = df_filtered['data'].dt.hour
    order = list(range(24))

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

# Normalizar valores dos indicadores
df_normalized = df_filtered.copy()
for poluente in selectbox_poluentes:
    min_val = df_normalized[poluente].min()
    max_val = df_normalized[poluente].max()
    df_normalized[poluente] = (df_normalized[poluente] - min_val) / (max_val - min_val)

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

df_normalized.sort_values(by=[orderby_column], inplace=True, ascending=orderby_asc)

# Função para identificar o máximo de forma segura
def safe_idxmax(series):
    if series.notna().any():
        return series.idxmax()
    return None

# Checkbox para alternar entre médias combinadas e separadas
view_combined = st.sidebar.checkbox('Ver Médias Combinadas', value=True)

tabs = st.tabs(["Todas"] + selectbox_estacao) if view_combined else st.tabs(selectbox_estacao)

for tab, estacao in zip(tabs, ["Todas"] + selectbox_estacao if view_combined else selectbox_estacao):
    with tab:
        if view_combined and estacao == "Todas":
            st.subheader("Todas as Estações")
            df_estacao = df_normalized
        else:
            st.subheader(f'Estação: {estacao}')
            df_estacao = df_normalized[df_normalized['Estação'] == estacao]

        col1, col2 = st.columns(2)
        col1.metric("Mediçōes", df_estacao[selectbox_poluentes].count().sum())
        col2.metric("Concentração Total de Matéria", human_format(df_estacao[selectbox_poluentes].sum().sum()))

        for poluente in selectbox_poluentes:
            with st.expander(f"Indicador: {poluente}", expanded=True):
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric(f"Mediçōes de {poluente}", df_estacao[poluente].count())
                with col2:
                    st.metric(f"Concentração Total de {poluente}", human_format(df_estacao[poluente].sum()))
                with col3:
                    max_period_label = "N/A"
                    if not df_estacao.empty:
                        if granularity == 'Ano':
                            max_period = safe_idxmax(df_estacao.groupby(df_estacao['data'].dt.year)[poluente].mean())
                            max_period_label = f"Ano: {max_period}" if max_period is not None else "N/A"
                        elif granularity == 'Mês':
                            max_period = safe_idxmax(df_estacao.groupby(df_estacao['data'].dt.month)[poluente].mean())
                            max_period_label = f"Mês: {max_period}" if max_period is not None else "N/A"
                        elif granularity == 'Dia':
                            max_period = safe_idxmax(df_estacao.groupby(df_estacao['data'].dt.date)[poluente].mean())
                            max_period_label = f"Dia: {max_period}" if max_period is not None else "N/A"
                        elif granularity == 'Hora':
                            max_period = safe_idxmax(df_estacao.groupby(df_estacao['data'].dt.hour)[poluente].mean())
                            max_period_label = f"Hora: {max_period}" if max_period is not None else "N/A"

                    col3.metric("Período com Média mais Alta", max_period_label)
                if view_combined and estacao == "Todas":
                    with col4:
                        max_station = safe_idxmax(df_normalized.groupby('Estação')[poluente].mean())
                        col4.metric(f"Estação com Média mais Alta de {poluente}", max_station if max_station is not None else "N/A")

                # Gráfico de barras para o indicador
                if granularity == 'Ano':
                    df_grouped = df_estacao.groupby(df_estacao['data'].dt.year)[poluente].mean()
                    df_grouped.index.name = 'Ano'
                elif granularity == 'Mês':
                    df_grouped = df_estacao.groupby(df_estacao['data'].dt.month)[poluente].mean()
                    df_grouped.index.name = 'Mês'
                elif granularity == 'Dia':
                    df_grouped = df_estacao.groupby(df_estacao['data'].dt.date)[poluente].mean()
                    df_grouped.index.name = 'Dia'
                elif granularity == 'Hora':
                    df_grouped = df_estacao.groupby(df_estacao['data'].dt.hour)[poluente].mean()
                    df_grouped.index.name = 'Hora'
                
                st.bar_chart(df_grouped, height=300, use_container_width=True)
                st.caption(f'Média do indicador {poluente} - {estacao}')

# Gráfico geográfico
with st.expander("Visão Geográfica"):
    tabs_geo = st.tabs(["Todos"] + selectbox_poluentes)
    for tab, poluente in zip(tabs_geo, ["Todos"] + selectbox_poluentes):
        with tab:
            if poluente == "Todos":
                df_station_means = df_normalized.groupby(['Estação', 'Latitude', 'Longitude'])[selectbox_poluentes].mean().reset_index()
                # Criar string de indicadores para o tooltip
                df_station_means['tooltip'] = df_station_means.apply(
                    lambda row: '\n'.join([f"{p}: {row[p]:.2f}" if not pd.isna(row[p]) else f"{p}: --" for p in selectbox_poluentes]),
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
            else:
                df_station_means = df_normalized.groupby(['Estação', 'Latitude', 'Longitude'])[poluente].mean().reset_index()
                df_station_means['normalized'] = (df_station_means[poluente] - df_station_means[poluente].min()) / (df_station_means[poluente].max() - df_station_means[poluente].min())

                try:
                    df_station_means['color'] = df_station_means['normalized'].apply(lambda x: [int(x * 255), 0, int((1 - x) * 255), 150])
                except ValueError:
                    df_station_means.dropna(subset=['normalized'], inplace=True)
                    df_station_means['color'] = df_station_means['normalized'].apply(lambda x: [int(x * 255), 0, int((1 - x) * 255), 150])

                df_station_means['tooltip'] = df_station_means.apply(
                    lambda row: f"{poluente}: {row[poluente]:.2f}" if not pd.isna(row[poluente]) else f"{poluente}: --",
                    axis=1
                )
                layer = pdk.Layer(
                    'ScatterplotLayer',
                    df_station_means,
                    get_position=['Longitude', 'Latitude'],
                    get_radius=500,
                    get_fill_color='color',
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

# Gráfico de calor para evolução dos indicadores por estação
with st.expander("Evolução dos Indicadores por Estação (Heatmap)"):
    for poluente in selectbox_poluentes:
        df_heatmap = df_normalized.pivot_table(values=poluente, index='Estação', columns='tempo')
        fig = px.imshow(df_heatmap, aspect='auto', color_continuous_scale='RdBu_r', title=f'Evolução do indicador {poluente} por Estação')
        st.plotly_chart(fig)

# Gráfico de linhas para médias normalizadas
with st.expander("Médias Normalizadas ao Longo do Tempo"):
    df_line = df_normalized.groupby(['tempo'])[selectbox_poluentes].mean().reset_index()
    df_line_normalized = (df_line[selectbox_poluentes] - df_line[selectbox_poluentes].min()) / (df_line[selectbox_poluentes].max() - df_line[selectbox_poluentes].min())
    df_line_normalized['tempo'] = df_line['tempo'].astype(str)

    if order is not None:
        df_line_normalized['tempo'] = pd.Categorical(df_line_normalized['tempo'], categories=order, ordered=True)

    df_line_normalized = df_line_normalized.sort_values('tempo')
    st.line_chart(df_line_normalized.set_index('tempo'))

# Matriz de correlação
with st.expander("Matriz de Correlação"):
    if not df_normalized[selectbox_poluentes].empty:
        corr_matrix = df_normalized[selectbox_poluentes].corr()
        fig, ax = plt.subplots(figsize=(10, 3))
        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', ax=ax)
        st.pyplot(fig, use_container_width=False)
    else:
        st.write("Sem dados suficientes para calcular a matriz de correlação.")

# Visualização dos dados
with st.expander("Tabela"):
    st.dataframe(df_normalized[['data', 'Estação', 'Latitude', 'Longitude'] + selectbox_poluentes])
