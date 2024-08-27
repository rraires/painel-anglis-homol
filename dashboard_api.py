import streamlit as st
import json
import psycopg2
import pandas as pd
from datetime import datetime, timedelta
import requests
import time
import plotly.graph_objects as go
import plotly.express as px
# import pytz
# from jsonpath_ng.ext import parse

st.set_page_config(layout='wide')

col1, col2, col3 = st.columns([1,1,4])
col1.image('logo_anglis-bg.png', width=120)
col3.subheader('Consulta dados Históricos')

# Função para converter timestamp para datetime no formato ISO 8601
def convert_timestamp(timestamp):
    dt = datetime.utcfromtimestamp(timestamp) - timedelta(hours=3)  # Converter para GMT-3
    return dt.strftime('%d-%m-%Y %H:%M:%S')

# Função para converter data humada para timestamp EPOCH
def convert_data_humana(date_str):
    try:
      date_obj = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
    except ValueError:
      date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    # date_obj = date_obj + timedelta(hours=3)
    epoch_time = int(date_obj.timestamp())
    return epoch_time

# Função para coletar os dados do Banco
@st.cache_data
def coleta_banco(data_inicio, data_fim):
    # Conectar ao banco de dados PostgreSQL
    conn = psycopg2.connect(
        host="reports.anglis.com.br",
        database="anglismonitoramento",
        user="anglisdbadm",
        password="anglis777power144"
    )
    cur = conn.cursor()

    timestamp_start = convert_data_humana(data_inicio)
    timestamp_end = convert_data_humana(data_fim)

    # Ler X Registros
    # Executar a consulta para ler uma amostra de registros filtrados por timestamp
    cur.execute('''
        SELECT * FROM dados_json
        WHERE timestamp BETWEEN %s AND %s;
    ''', (timestamp_start, timestamp_end))

    # Obter todos os resultados
    rows = cur.fetchall()

    # Obter os nomes das colunas
    colnames = [desc[0] for desc in cur.description]

    # Converter os resultados para um DataFrame do Pandas
    df = pd.DataFrame(rows, columns=colnames)
 
    # Fechar a conexão
    cur.close()
    conn.close()

    return df



# Função para extrair os dados do JSON
def extrair_dados(json_str):
    try:
        dados = json.loads(json_str)
        for item in dados:
            if item.get('Franquia') == selecao_franquia:
              for residente in item.get('Residentes', []):
                if residente.get('Residente') == selecao_residente:
                  for comodo in residente.get('comodos', []):
                    if comodo.get('comodo') == selecao_comodo:
                      people = comodo.get('people')
                      mov = comodo.get('mov')
                      veloc = comodo.get('veloc')
                      queda = comodo.get('queda')
                      alarme_id = comodo.get('alarme_id')
                      if comodo.get('areas', []) != None and comodo.get('areas', []) != []:
                        for area in comodo.get('areas', []):
                          if area.get('nome') == selecao_area:
                            presenc_area = area.get("presenc")
                            mov_area = area.get("mov_area")
                            deitada = area.get("deitada")
                            sensor_mov = area.get("sensor_mov")
                      if comodo.get('obj', []) != None and comodo.get('obj', []) != []:
                        for obj in comodo.get('obj', []):
                          if obj.get('label') == 'Colaborador':
                            colaborador = 1
                          else:
                            colaborador = 0
                      else:
                        colaborador = 0
        try:
          return {
                  "people": people,
                  "mov": mov,
                  "veloc": veloc,
                  "queda": queda,
                  "alarme_id": alarme_id,
                  "presenc_area": presenc_area,
                  "mov_area": mov_area,
                  "deitada": deitada,
                  "sensor_mov": sensor_mov,
                  "colaborador": colaborador
                }
        except:
          return {
                  "people": people,
                  "mov": mov,
                  "veloc": veloc,
                  "queda": queda,
                  "alarme_id": alarme_id
                }
          

    except json.JSONDecodeError as e:
      print(f"Erro ao decodificar JSON: {e}")
    # return {"people": None, "mov": None, "queda": None}


def gera_grafico(df_extracted):
    fig = go.Figure()
    try:
        fig.add_trace(go.Scatter(x=df_extracted.timestamp, y=df_extracted['people'], name='Presença'))
        fig.add_trace(go.Scatter(x=df_extracted.timestamp, y=df_extracted['mov'], name='Movimento'))
        fig.add_trace(go.Scatter(x=df_extracted.timestamp, y=df_extracted['queda'], name='Queda'))
        fig.add_trace(go.Scatter(x=df_extracted.timestamp, y=df_extracted['alarme_id'], name='alarme_id'))
        fig.add_trace(go.Scatter(x=df_extracted.timestamp, y=df_extracted['presenc_area'], name='Presença Area'))
        fig.add_trace(go.Scatter(x=df_extracted.timestamp, y=df_extracted['mov_area'], name='Movimento Area'))
        fig.add_trace(go.Scatter(x=df_extracted.timestamp, y=df_extracted['deitada'], name='Deitada'))
        fig.add_trace(go.Scatter(x=df_extracted.timestamp, y=df_extracted['sensor_mov'], name='Sensor Movimento'))
        fig.add_trace(go.Scatter(x=df_extracted.timestamp, y=df_extracted['colaborador'], name='Colaborador'))
    except:
        fig.add_trace(go.Scatter(x=df_extracted.timestamp, y=df_extracted['people'], name='Presença'))
        fig.add_trace(go.Scatter(x=df_extracted.timestamp, y=df_extracted['mov'], name='Movimento'))
        fig.add_trace(go.Scatter(x=df_extracted.timestamp, y=df_extracted['queda'], name='Queda'))
        fig.add_trace(go.Scatter(x=df_extracted.timestamp, y=df_extracted['alarme_id'], name='alarme_id'))

    fig.update_layout(title='Graficos')

    st.plotly_chart(fig)


url = 'http://app.anglis.com.br:8081/monit'
response = requests.get(url)
data_api = response.json()

with st.expander('Seleciona o Cliente:', expanded=True):
    col1, col2, col3, col4 = st.columns(4)
    franquias = [record.get("Franquia") for record in data_api]
    selecao_franquia = col1.selectbox("Franquia", franquias)
    dados_residentes_franquia = [record.get("Residentes") for record in data_api if record.get("Franquia") == selecao_franquia]
    residentes_franquia = [record.get("Residente") for record in dados_residentes_franquia[0]]
    selecao_residente = col2.selectbox('Residente', residentes_franquia, key='residente')
    dados_residente = [record for record in dados_residentes_franquia[0] if record.get("Residente") == selecao_residente]
    comodos_residente = [record.get("comodo") for record in dados_residente[0]['comodos']]
    selecao_comodo = col3.selectbox('Cômodo', comodos_residente, key='comodo')
    dados_comodo = [record for record in dados_residente[0]['comodos'] if record.get("comodo") == selecao_comodo]
    areas_comodo = [record.get("nome") for record in dados_comodo[0]['areas']]
    selecao_area = col4.selectbox('Área', areas_comodo, key='area')

with st.form('Data input'):
    col1, col2 = st.columns(2)
    date1 = col1.date_input('Selecione data 1', format="DD/MM/YYYY")
    # date2 = col2.date_input('Selecione data 2', format="DD/MM/YYYY")

    if st.form_submit_button('Submit'):
        # st.write(selecao_franquia)
        # st.write(selecao_residente)
        # st.write(selecao_comodo)
        # st.write(selecao_area)
        # st.write(date1)
        # st.write(date1 + timedelta(days=1))

        data_inicio = str(date1)
        data_fim = str(date1 + timedelta(days=1))

        # Marca o tempo inicial
        start_time = time.time()
        df_bruto = coleta_banco(data_inicio, data_fim)
        # Aplicar a função para extrair os dados
        df_extracted = df_bruto['json_data'].apply(extrair_dados)
        # Expandir os dicionários em colunas e adicionar a coluna timestamp
        df_extracted = pd.concat([df_bruto['timestamp'], pd.json_normalize(df_extracted)], axis=1)
        # Aplicar a função para converter os timestamps
        df_extracted['timestamp'] = df_bruto['timestamp'].apply(convert_timestamp)
        df_extracted['timestamp'] = pd.to_datetime(df_extracted['timestamp'], format='%d-%m-%Y %H:%M:%S')
        df_extracted = df_extracted.fillna(0)
        st.write(df_extracted)
        gera_grafico(df_extracted)
        # Marca o tempo final
        end_time = time.time()
        execution_time = end_time - start_time
        st.write('Tempo de execução: ', execution_time, ' segundos')


        #############################################3

        coluna = 'presenc_area'
        
        # Considerar 0 apenas com periodos de 0 acima de X minutos (Cama por exemplo)

        df_tratado = df_extracted.copy()

        # Converter a coluna 'timestamp' para datetime
        df_tratado['timestamp'] = pd.to_datetime(df_tratado['timestamp'])

        # Ordenar os dados por timestamp para garantir a sequência correta
        df_tratado = df_tratado.sort_values('timestamp').reset_index(drop=True)

        # Identificar os períodos de ausência (presenca_comodo == 0)
        df_tratado['absence'] = (df_tratado[coluna] == 0).astype(int)

        # Calcular a duração de cada período de ausência
        df_tratado['absence_block'] = (df_tratado['absence'].diff(1) != 0).cumsum()
        absence_durations = df_tratado[df_tratado['absence'] == 1].groupby('absence_block')['timestamp'].agg(['min', 'max'])
        absence_durations['duration'] = absence_durations['max'] - absence_durations['min']

        # Filtrar apenas as ausências que duram mais de 5 minutos
        long_absences = absence_durations[absence_durations['duration'] > pd.Timedelta(minutes=10)]

        # Criar uma máscara para identificar quais períodos de ausência são longos
        long_absence_blocks = long_absences.index.tolist()
        df_tratado['valid_absence'] = df_tratado['absence_block'].isin(long_absence_blocks)

        # Atualizar a coluna de presença para desconsiderar ausências curtas (substituir por 1)
        df_tratado.loc[(df_tratado['absence'] == 1) & (~df_tratado['valid_absence']), coluna] = 1

        # Remover colunas auxiliares
        df_tratado = df_tratado.drop(columns=['absence', 'absence_block', 'valid_absence'])


        # Criar dataframe dos blocos

        # Filtrar os períodos de presença (presenca_comodo == 1)
        df_presence = df_tratado[df_tratado[coluna] == 1].copy()

        # Agrupar os dados para criar blocos contínuos de tempo
        df_presence['block'] = (df_presence['timestamp'].diff() > pd.Timedelta(minutes=10)).cumsum()

        # Encontrar início e fim de cada bloco
        presence_blocks = df_presence.groupby(['block']).agg(
            Start=('timestamp', 'min'),
            End=('timestamp', 'max')
        ).reset_index()

        # Extrair a hora do dia e o dia da semana para plotagem
        presence_blocks['start_hour'] = presence_blocks['Start'].dt.hour + presence_blocks['Start'].dt.minute / 60
        presence_blocks['end_hour'] = presence_blocks['End'].dt.hour + presence_blocks['End'].dt.minute / 60
        presence_blocks['day_of_week'] = presence_blocks['Start'].dt.day_name()

        # Mapeamento dos dias da semana em português
        day_translation = {
            'Monday': 'Seg',
            'Tuesday': 'Ter',
            'Wednesday': 'Qua',
            'Thursday': 'Qui',
            'Friday': 'Sex',
            'Saturday': 'Sab',
            'Sunday': 'Dom'
        }
        presence_blocks['day_of_week'] = presence_blocks['day_of_week'].map(day_translation)

        df = presence_blocks.copy()

        # Converter colunas Start e End para datetime
        df['Start'] = pd.to_datetime(df['Start'])
        df['End'] = pd.to_datetime(df['End'])

        # Criar uma data fictícia base (por exemplo, 2024-01-01) para usar com horários
        df['Start_time'] = pd.to_datetime('2024-01-01 ' + df['Start'].dt.strftime('%H:%M:%S'))
        df['End_time'] = pd.to_datetime('2024-01-01 ' + df['End'].dt.strftime('%H:%M:%S'))

        # Plotar o gráfico de Gantt usando o Plotly
        fig = px.timeline(df, x_start="Start_time", x_end="End_time", y="day_of_week", color="day_of_week")

        # Customizar o gráfico
        fig.update_traces(marker_color='skyblue')  # Define uma cor fixa para todas as barras
        fig.update_traces(opacity=1)  # Define a opacidade das barras


        # Customizar o gráfico
        fig.update_layout(
            xaxis=dict(
                tickformat="%H:%M",
                range=[pd.to_datetime('2024-01-01 00:00:00'), pd.to_datetime('2024-01-01 23:59:59')]
            ),
            xaxis_title="Horário do Dia",
            yaxis_title="Dia da Semana",
            title="Presença Cama",
            height=400,
            showlegend=False
        )

        # Adicionar linhas horizontais para separar os dias
        days = df['day_of_week'].unique()
        for day in days:
            fig.add_shape(
                type="line",
                x0=df['Start_time'].min(), x1=df['End_time'].max(),
                y0=day, y1=day,
                line=dict(color="Gray", width=0.5, dash="dot")
            )


        # Exibir o gráfico
        st.plotly_chart(fig)

        df = presence_blocks.copy()

        # Converter colunas Start e End para datetime
        df['Start'] = pd.to_datetime(df['Start'])
        df['End'] = pd.to_datetime(df['End'])

        # Calcular a duração de cada visita
        df['Duration'] = (df['End'] - df['Start']).dt.total_seconds()

        # Calcular o número de visitas
        num_visits = len(df)

        # Calcular o maior e menor período de presença
        longest_visit = df['Duration'].max()
        shortest_visit = df['Duration'].min()

        # Calcular a média de tempo por visita
        average_visit = df['Duration'].mean()

        # Converter os períodos de segundos para uma forma mais legível (horas, minutos, segundos)
        import datetime

        longest_visit_str = str(datetime.timedelta(seconds=int(longest_visit)))
        shortest_visit_str = str(datetime.timedelta(seconds=int(shortest_visit)))
        average_visit_str = str(datetime.timedelta(seconds=int(average_visit)))

        st.write(f"Estatísticas de Resumo:")
        st.write(f"Número de Vezes: {num_visits}")
        st.write(f"Maior Período de Presença: {longest_visit_str}")
        st.write(f"Menor Período de Presença: {shortest_visit_str}")
        st.write(f"Média de Tempo: {average_visit_str}")
