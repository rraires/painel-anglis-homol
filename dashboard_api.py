import streamlit as st
import json
import psycopg2
import pandas as pd
from datetime import datetime, timedelta
import requests
import time
import plotly.graph_objects as go
import plotly.express as px
import re

st.set_page_config(layout='wide')
st.logo("media/logo_anglis-bg.png", size='large')

# Função para converter timestamp para datetime no formato ISO 8601
def convert_timestamp(timestamp):
    # dt = datetime.utcfromtimestamp(timestamp) - timedelta(hours=3)  # Converter para GMT-3
    return dt.strftime('%d-%m-%Y %H:%M:%S')

# Função para converter data humada para timestamp EPOCH
def convert_data_humana(date_str):
    try:
      date_obj = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
    except ValueError:
      date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    date_obj = date_obj + timedelta(hours=3)
    epoch_time = int(date_obj.timestamp())
    return epoch_time

# Função para coletar os dados do Banco
@st.cache_data
def coleta_banco(data_inicio, data_fim):
  # Conectar ao banco de dados PostgreSQL
  conn = psycopg2.connect(
      host="reports.anglis.com.br",
      database="anglismonitoramento",
      user="acessopuc",
      password="@ngl15123"
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
  return df

  # Fechar a conexão
  cur.close()
  conn.close()

@st.cache_data
def tabelao(json_str, codId_franquia):
    # Criar o Tabelão

    # json_str = data

    lista_dataframe = []
    qtde_pessoas_llm = 0
    queda_llm=0
    presenca_enfermeiros = 0
    qtde_enfermeiros = 0
    poses_llm=[]
    acao_enfermeiro = ""
    classificacao_acao = ""
    queda_conf = 0
    presenca_cama = {}
    presenca_residente = 0
    residente_conf = 0

    #Coletar dados da raiz do Comodo
    for dados in json_str:
        dados = json.loads(dados)
        for item in dados:
            if item.get('codId') == codId_franquia:
                # st.write('2: ', item)
                for residente in item.get('Residentes', []):
                    # st.write('3: ', residente)
                    for comodo in residente.get('comodos', []):
                        timestamp = item.get('timestamp')
                        codId_franquia = item.get('codId')
                        franquia = item.get('Franquia')
                        codId_residente = residente.get('codId')
                        cliente = residente.get('Residente')
                        deviceId = comodo.get('deviceId')
                        device = comodo.get('comodo')
                        local = comodo.get('local')
                        people = comodo.get('people')
                        # mov = comodo.get('mov')
                        queda = comodo.get('queda')
                        if "queda_conf" in comodo:
                            queda_conf = comodo.get('queda_conf')
                        if comodo.get('obj', []) != None and comodo.get('obj', []) != []:
                            for obj in comodo.get('obj', []):
                                if 'Colaborador' in obj.get('label', ''):
                                    colaborador = 1
                                else:
                                    colaborador = 0
                                if obj.get('label') == 'Pessoa':
                                    pessoa = 1
                                else:
                                    pessoa = 0
                        else:
                            colaborador = 0
                            pessoa = 0
                        if "llm" in comodo:
                            llm = comodo.get('llm')
                            if comodo.get('llm') != None and comodo.get('llm') != [] and len(llm) != 1:
                                qtde_pessoas_llm = llm["quantidade_pessoas"]
                                try:
                                    queda_llm = llm["queda_detectada"]
                                except:
                                    queda_llm = llm["queda_detecada"]
                                presenca_enfermeiros = llm["presenca_enfermeiros_cuidadores"]
                                qtde_enfermeiros = llm["quantidade_enfermeiros_cuidadores"]
                                poses_llm = llm["poses"]
                                acao_enfermeiro = llm["acao_enfermeiros_cuidadores"]
                                if 'classificacao_acao' in llm:
                                    classificacao_acao = llm["classificacao_acao"]
                                if "presenca_cama" in llm:
                                    presenca_cama = llm["presenca_cama"]
                                if llm.get('bounding_boxes_pessoas') != []:
                                    for llm_pessoa in llm.get('bounding_boxes_pessoas'):
                                        try:
                                            if llm_pessoa[4] == "RESIDENTE_1":
                                                presenca_residente = 1
                                                residente_conf = float(llm_pessoa[5])
                                        except:
                                            continue
                            else:
                                qtde_pessoas_llm = 0
                                queda_llm=0
                                presenca_enfermeiros = 0
                                qtde_enfermeiros = 0
                                poses_llm=[]
                                acao_enfermeiro = ""
                                classificacao_acao = ""
                                presenca_cama = {}
                                queda_conf = 0
                                presenca_residente = 0
                                residente_conf = 0

                        resultado = {
                                "timestamp": timestamp,
                                "codId_franquia": codId_franquia,
                                "franquia": franquia,
                                "codId_residente": codId_residente,
                                "residente": cliente,
                                "deviceId": deviceId,
                                "device": device,
                                "local": local,
                                "area": 'comodo',
                                "people": people,
                                # "mov": mov,
                                "queda": queda,
                                "queda_conf": queda_conf,
                                "colaborador": colaborador,
                                "pessoa": pessoa,
                                "presenc": 0,
                                "mov_area": 0,
                                "deitada": 0,
                                "qtde_pessoas_llm": qtde_pessoas_llm,
                                "queda_llm": queda_llm,
                                "presenca_enfermeiros": presenca_enfermeiros,
                                "qtde_enfermeiros": qtde_enfermeiros,
                                "poses_llm": poses_llm,
                                "acao_enfermeiro": acao_enfermeiro,
                                "classificacao_acao": classificacao_acao,
                                "presenca_cama": presenca_cama,
                                "presenca_residente": presenca_residente,
                                "residente_conf": residente_conf
                            }
                        lista_dataframe.append(resultado)


        #Coletar dados das areas
        for item in dados:
            # print('1: ', item)
            if item.get('codId') == codId_franquia:
                # print('2: ', item)
                for residente in item.get('Residentes', []):
                    # print('3: ', residente)
                    for comodo in residente.get('comodos', []):
                        if comodo.get('areas', []) != None and comodo.get('areas', []) != [] and comodo.get('areas', []) != 'comodo':
                            for area in comodo.get('areas', []):
                                if not area.get('nome', '').startswith('_'):
                                    timestamp = item.get('timestamp')
                                    codId_franquia = item.get('codId')
                                    franquia = item.get('Franquia')
                                    codId_residente = residente.get('codId')
                                    cliente = residente.get('Residente')
                                    deviceId = comodo.get('deviceId')
                                    device = comodo.get('comodo')
                                    local = comodo.get('local')
                                    nome_area = area.get('nome')
                                    presenc = area.get("presenc")
                                    mov_area = area.get("mov_area")
                                    deitada = area.get("deitada")
                                    sensor_mov = area.get("sensor_mov")

                                    resultado = {
                                        "timestamp": timestamp,
                                        "codId_franquia": codId_franquia,
                                        "franquia": franquia,
                                        "codId_residente": codId_residente,
                                        "residente": cliente,
                                        "deviceId": deviceId,
                                        "device": device,
                                        "local": local,
                                        "area": nome_area,
                                        "people": 0,
                                        # "mov": 0,
                                        "queda": 0,
                                        "queda_conf": 0,
                                        "colaborador": 0,
                                        "pessoa": 0,
                                        "presenc": presenc,
                                        "mov_area": mov_area,
                                        "deitada": deitada,
                                        "sensor_mov": sensor_mov,
                                        "qtde_pessoas_llm": 0,
                                        "queda_llm": False,
                                        "presenca_enfermeiros": 0,
                                        "qtde_enfermeiros": 0,
                                        "poses_llm": [],
                                        "acao_enfermeiro": "",
                                        "classificacao_acao": "",
                                        "presenca_cama": {},
                                        "presenca_residente": 0,
                                        "residente_conf": 0                                        
                                        }
                                    lista_dataframe.append(resultado)


    df_extracted = pd.DataFrame(lista_dataframe)
    df_extracted['timestamp'] = df_extracted['timestamp'].astype(int)
    # Ordenar os dados por timestamp para garantir a sequência correta
    df_extracted = df_extracted.sort_values('timestamp').reset_index(drop=True)

    # Converter o Timestamp de formato Epoch para formato Y/M/D
    df_extracted['timestamp'] = pd.to_datetime(df_extracted['timestamp'], unit='s') - pd.Timedelta(hours=3)

    # Dados de Presenca Cama pela LLM
    df_extracted['presenca_cama_flag'] = df_extracted['presenca_cama'].apply(lambda x: 1 if 'Ocupada' in str(x) else 0)

    # # Lista de palavras a serem verificadas
    # palavras_chave = ['Ocupada', 'ocupada', 'Ocupado', 'ocupado']

    # # Criar a flag usando regex para correspondência exata
    # df_extracted['presenca_cama_flag'] = df_extracted['presenca_cama'].apply(lambda x: 1 if any(re.search(r'\b' + palavra + r'\b', str(x)) for palavra in palavras_chave) else 0)

    # Lista de palavras-chave e palavras de negação
    palavras_chave_cama = ['Ocupada', 'ocupada', 'Ocupado', 'ocupado']
    negacoes_cama = ['não', 'nao', 'Não', 'Nao']

    # Criar a flag considerando negações
    def verificar_presenca_cama(texto):
        texto = str(texto)  # Converter para string caso não seja
        for palavra in palavras_chave_cama:
            # Verificar se a palavra-chave aparece sem estar precedida por negação
            if re.search(rf'\b({"|".join(negacoes_cama)})\s+{palavra}\b', texto):
                return 0  # Ignorar casos com negação
            if re.search(rf'\b{palavra}\b', texto):
                return 1  # Encontrou sem negação
        return 0

    df_extracted['presenca_cama_flag'] = df_extracted['presenca_cama'].apply(verificar_presenca_cama)

    # Lista de palavras-chave e palavras de negação
    palavras_chave_pose = ['Deitada', 'deitada', 'Deitado', 'deitado']
    negacoes_pose = ['não', 'nao', 'Não', 'Nao']

    # Criar a flag considerando negações
    def verificar_pose(texto):
        texto = str(texto)  # Converter para string caso não seja
        for palavra in palavras_chave_pose:
            # Verificar se a palavra-chave aparece sem estar precedida por negação
            if re.search(rf'\b({"|".join(negacoes_pose)})\s+{palavra}\b', texto):
                return 0  # Ignorar casos com negação
            if re.search(rf'\b{palavra}\b', texto):
                return 1  # Encontrou sem negação
        return 0

    df_extracted['pose_deitado'] = df_extracted['poses_llm'].apply(verificar_pose)

    df_extracted['queda_llm'] = df_extracted['queda_llm'].astype(int)

    return df_extracted

@st.cache_data
def processar_blocos(df_extracted):
    # Tempo entre eventos (> que x minutos)
    tempo_entre_eventos = 5 # minutos

    # Tempo dos eventos (Considerar apenas eventos maiores que x segundos)
    tempo_eventos = 120 # segundos

    # Considerar 0 apenas com periodos de 0 acima de X minutos (Cama por exemplo)
    # df_tratado = df_extracted.copy()

    df_split_consolidado = pd.DataFrame()

    residente_unique = df_extracted['residente'].unique()
    for residente in residente_unique:
        local_unique = df_extracted[df_extracted['residente'] == residente]['local'].unique()
        for local in local_unique:
            area_unique = df_extracted[(df_extracted['residente'] == residente) & (df_extracted['local'] == local)]['area'].unique()
            for area in area_unique:
                # print(residente, local, area)
                df_tratado = df_extracted[(df_extracted['residente'] == residente) & (df_extracted['local'] == local) & (df_extracted['area'] == area)].copy()
                for coluna in df_tratado.columns:
                    # if coluna != 'timestamp' and coluna != 'alarme_id':
                    if coluna  in ['people', 'mov', 'queda', 'colaborador', 'pessoa' ,'presenc', 'mov_area', 'deitada','qtde_pessoas_llm', 'presenca_enfermeiros', 'presenca_cama_flag', 'pose_deitado', 'presenc_residente' ]:

                        # Identificar os períodos de ausência (presenca_comodo == 0)
                        df_tratado['absence'] = (df_tratado[coluna] == 0).astype(int)

                        # Calcular a duração de cada período de ausência
                        df_tratado['absence_block'] = (df_tratado['absence'].diff(1) != 0).cumsum()
                        absence_durations = df_tratado[df_tratado['absence'] == 1].groupby('absence_block')['timestamp'].agg(['min', 'max'])
                        absence_durations['duration'] = absence_durations['max'] - absence_durations['min']

                        # Filtrar apenas as ausências que duram mais de X minutos
                        long_absences = absence_durations[absence_durations['duration'] > pd.Timedelta(minutes=tempo_entre_eventos)]

                        # Criar uma máscara para identificar quais períodos de ausência são longos
                        long_absence_blocks = long_absences.index.tolist()
                        df_tratado['valid_absence'] = df_tratado['absence_block'].isin(long_absence_blocks)

                        # Atualizar a coluna de presença para desconsiderar ausências curtas (substituir por 1)
                        df_tratado.loc[(df_tratado['absence'] == 1) & (~df_tratado['valid_absence']), coluna] = 1

                        # Remover colunas auxiliares
                        df_tratado = df_tratado.drop(columns=['absence', 'absence_block', 'valid_absence'])

                # Criar dataframe dos blocos

                presence_blocks = pd.DataFrame(columns=['block','Start', 'End', 'Evento'])

                for coluna in df_tratado.columns:
                    # if coluna != 'timestamp' and coluna != 'alarme_id':
                    if coluna  in ['people', 'mov', 'queda',  'colaborador', 'pessoa' , 'presenc', 'mov_area', 'deitada', 'qtde_pessoas_llm', 'presenca_enfermeiros', 'presenca_cama_flag', 'pose_deitado', 'presenca_residente']:

                        # Filtrar os períodos de presença (presenca_comodo == 1)
                        df_presence = df_tratado[df_tratado[coluna] == 1].copy()

                        # Agrupar os dados para criar blocos contínuos de tempo
                        df_presence['block'] = (df_presence['timestamp'].diff() > pd.Timedelta(minutes=10)).cumsum()

                        # Encontrar início e fim de cada bloco
                        presence_blocks_temp = df_presence.groupby(['block', 'codId_franquia', 'franquia',	'codId_residente',	'residente',	'local',	'area']).agg(
                            Start=('timestamp', 'min'),
                            End=('timestamp', 'max')
                        ).reset_index()
                        presence_blocks_temp['Evento'] = coluna
                        presence_blocks = pd.concat([presence_blocks, presence_blocks_temp], ignore_index=True)


                # Dividir os Blocos que passam de um dia para o outr0
                
                df_split= presence_blocks.copy()

                # Converter novamente colunas start e end para datetime
                df_split['Start'] = pd.to_datetime(df_split['Start'])
                df_split['End'] = pd.to_datetime(df_split['End'])

                # Calcular a duração de cada evento
                df_split['Duration'] = (df_split['End'] - df_split['Start']).dt.total_seconds()

                # Considerar apenas eventos com mais de X segundos
                df_split = df_split[df_split['Duration'] > tempo_eventos]

                # Atualizando a coluna 'block' para ter uma sequência contínua
                df_split['block'] = range(len(df_split))


                # Extrair a hora do dia e o dia da semana para plotagem
                df_split['start_hour'] = df_split['Start'].dt.hour + df_split['Start'].dt.minute / 60
                df_split['end_hour'] = df_split['End'].dt.hour + df_split['End'].dt.minute / 60
                df_split['day_of_week'] = df_split['Start'].dt.day_name()

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
                df_split['day_of_week'] = df_split['day_of_week'].map(day_translation)

                df_split_consolidado = pd.concat([df_split_consolidado, df_split], ignore_index=True)


    return df_split_consolidado

def coleta_acoes(df_filtro):

    #filtro
    # df_filtro = df_extracted[(df_extracted['deviceId'] == filtro_deviceId) & (df_extracted['area'] == 'comodo')]

    # Load the uploaded CSV file
    # file_path = '/content/walter_captamed_02_12.csv'
    # data = pd.read_csv(file_path)
    data = df_filtro.copy().reset_index(drop=True)

    # Convert 'timestamp' to datetime format for easier processing
    data['timestamp'] = pd.to_datetime(data['timestamp'])

    # Extract the hour for grouping
    data['hour'] = data['timestamp'].dt.strftime('%Y-%m-%d %H:00')

    # Filter relevant columns
    actions_data = data[['hour', 'acao_enfermeiro']]

    # Converter todos os valores para strings antes de aplicar as operações
    actions_data['acao_enfermeiro'] = actions_data['acao_enfermeiro'].apply(lambda x: str(x) if not isinstance(x, str) else x)

    # Group by hour and aggregate the actions
    # Filtering out empty actions and summarizing text content
    actions_summary = (
        actions_data[actions_data['acao_enfermeiro'] != '[]']
        .groupby('hour')['acao_enfermeiro']
        .apply(lambda x: '. '.join(set(', '.join(x).replace('[', '').replace(']', '').split(', '))))
        .reset_index()
    )

    # Format the summary to match the requested format
    actions_summary['hour'] = pd.to_datetime(actions_summary['hour']).dt.strftime('%d/%m/%y %Hh')
    actions_summary.rename(columns={'hour': 'Hora', 'acao_enfermeiro': 'Acoes'}, inplace=True)
    return actions_summary

def coleta_acoes_classificadas(df_filtro):

    #filtro
    # df_filtro = df_extracted[(df_extracted['deviceId'] == filtro_deviceId) & (df_extracted['area'] == 'comodo')]

    # Load the uploaded CSV file
    # file_path = '/content/walter_captamed_02_12.csv'
    # data = pd.read_csv(file_path)
    data = df_filtro.copy().reset_index(drop=True)

    # Convert 'timestamp' to datetime format for easier processing
    data['timestamp'] = pd.to_datetime(data['timestamp'])

    # Extract the hour for grouping
    data['hour'] = data['timestamp'].dt.strftime('%Y-%m-%d %H:00')

    # Filter relevant columns
    actions_data = data[['hour', 'classificacao_acao']]

    # Converter todos os valores para strings antes de aplicar as operações
    actions_data['classificacao_acao'] = actions_data['classificacao_acao'].apply(lambda x: str(x) if not isinstance(x, str) else x)

    # Group by hour and aggregate the actions
    # Filtering out empty actions and summarizing text content
    actions_summary = (
        actions_data[actions_data['classificacao_acao'] != '[]']
        .groupby('hour')['classificacao_acao']
        .apply(lambda x: '. '.join(set(', '.join(x).replace('[', '').replace(']', '').split(', '))))
        .reset_index()
    )

    # Format the summary to match the requested format
    actions_summary['hour'] = pd.to_datetime(actions_summary['hour']).dt.strftime('%d/%m/%y %Hh')
    actions_summary.rename(columns={'hour': 'Hora', 'classificacao_acao': 'Acoes'}, inplace=True)
    return actions_summary


def grafico_dados_brutos(df_extracted):
    df_grafico = df_extracted.copy()

    fig = go.Figure()

    fig.add_trace(go.Scatter(x=df_grafico.timestamp, y=df_grafico['people'], name="people"))
    fig.add_trace(go.Scatter(x=df_grafico.timestamp, y=df_grafico['queda'], name="queda"))
    fig.add_trace(go.Scatter(x=df_grafico.timestamp, y=df_grafico['colaborador'], name="colaborador"))
    fig.add_trace(go.Scatter(x=df_grafico.timestamp, y=df_grafico['pessoa'], name="pessoa"))
    fig.add_trace(go.Scatter(x=df_grafico.timestamp, y=df_grafico['presenc'], name="presenc"))
    fig.add_trace(go.Scatter(x=df_grafico.timestamp, y=df_grafico['deitada'], name="deitada"))
    fig.add_trace(go.Scatter(x=df_grafico.timestamp, y=df_grafico['qtde_pessoas_llm'], name="qtde_pessoas_llm"))
    fig.add_trace(go.Scatter(x=df_grafico.timestamp, y=df_grafico['queda_llm'], name="queda_llm"))
    fig.add_trace(go.Scatter(x=df_grafico.timestamp, y=df_grafico['qtde_enfermeiros'], name="qtde_enfermeiros"))
    fig.add_trace(go.Scatter(x=df_grafico.timestamp, y=df_grafico['presenca_cama_flag'], name="presenca_cama_flag"))
    fig.add_trace(go.Scatter(x=df_grafico.timestamp, y=df_grafico['pose_deitado'], name="pose_deitado"))
    fig.add_trace(go.Scatter(x=df_grafico.timestamp, y=df_grafico['presenca_residente'], name="presenca_residente"))
    fig.add_trace(go.Scatter(x=df_grafico.timestamp, y=df_grafico['residente_conf'], name="residente_conf", yaxis='y2'))
    fig.add_trace(go.Scatter(x=df_grafico.timestamp, y=df_grafico['queda_conf'], name="queda_conf", yaxis='y2'))
    fig.add_trace(go.Scatter(x=df_grafico.timestamp, y=df_grafico['sensor_mov'], name='sensor_mov', yaxis='y2'))
    
    fig.update_layout(
        title=f"{df_grafico['residente'].iloc[0]} - {df_grafico['local'].iloc[0]}",
        xaxis_title='Timestamp',
        yaxis_title='Dados',
        yaxis2=dict(
            # title='sensor_mov e queda_conf',
            overlaying='y',
            side='right',
            showgrid=False  # Evita duplicação das linhas da grade
        ),
        # legend=dict(x=0.5, y=1.2, orientation='v'),
        )

    st.plotly_chart(fig)

def grafico_grantt(df):

    # GRÁFICO EVENTOS NO TEMPO (TRATADO)

    # df = df_split_consolidado.copy()
    # df = df_split_consolidado[(df_split_consolidado['codId_residente'] == filtro_codId_residente) & (df_split_consolidado['local'] == filtro_local) & (df_split_consolidado['area'] == 'comodo')]

    # Definindo a nova fake que será usada
    nova_data = "2024-08-01"

    # Ajustando as colunas Start e End para a nova data, mantendo os horários
    df['Start'] = df['Start'].apply(lambda x: pd.to_datetime(nova_data + ' ' + x.strftime('%H:%M:%S')))
    df['End'] = df['End'].apply(lambda x: pd.to_datetime(nova_data + ' ' + x.strftime('%H:%M:%S')))


    # Criando o gráfico de Gantt
    fig = px.timeline(df, x_start="Start", x_end="End", y="day_of_week", color="Evento",
                    # title=f"Atividade ao Longo do dia - {df_grafico['residente'].iloc[0]} - {df_grafico['local'].iloc[0]}",
                    category_orders={"Evento": ["colaborador", "queda_comodo"]},
                    labels={"day_of_week": "Dia da Semana"})

    # Formatando o eixo X para mostrar horas
    fig.update_layout(
        xaxis_title="Horário do Dia",
        xaxis=dict(
            type='date',
            tickformat='%H:%M:%S',
            range=[f"{nova_data} 00:00:00", f"{nova_data} 23:59:59"]  # Limita o eixo de 00:00 até 23:59
        ),
        width=1000,
        height=250
    )

    fig.update_yaxes(categoryorder="array", categoryarray= ["Dom", "Sab", "Sex", "Qui", "Qua", "Ter", "Seg"])

    # Ajustando a opacidade das barras para permitir visualização sobreposta
    fig.update_traces(opacity=0.6)  # A opacidade pode variar de 0 (totalmente transparente) a 1 (opaco)


    # Exibindo o gráfico
    st.plotly_chart(fig)

##############################################################################################

url = 'http://app.anglis.com.br:8081/monit'
response = requests.get(url)
data_api = response.json()


# Franquia
franquias = [record.get("Franquia") for record in data_api]
selecao_franquia = st.sidebar.selectbox("Franquia", franquias)
codId_franquia = [record.get("codId") for record in data_api if record.get("Franquia") == selecao_franquia]
dados_residentes_franquia = [record.get("Residentes") for record in data_api if record.get("codId") == codId_franquia[0]]

# Residente
residentes_franquia = [record.get("Residente") for record in dados_residentes_franquia[0]]
selecao_residente = st.sidebar.selectbox('Residente', residentes_franquia, key='residente')
codId_residente = [record.get("codId") for record in dados_residentes_franquia[0] if record.get("Residente") == selecao_residente]
dados_residente = [record for record in dados_residentes_franquia[0] if record.get("codId") == codId_residente[0]]

# Comodo / Device
comodos_residente = [record.get("local") for record in dados_residente[0]['comodos']]
selecao_comodo = st.sidebar.selectbox('Cômodo/Local', comodos_residente, key='comodo')
codId_comodo = [record.get("deviceId") for record in dados_residente[0]['comodos'] if record.get("local") == selecao_comodo]
dados_comodo = [record for record in dados_residente[0]['comodos'] if record.get("deviceId") == codId_comodo[0]]

# Área
areas_comodo = [record.get("nome") for record in dados_comodo[0]['areas']]
areas_comodo.insert(0,'comodo')
selecao_area = st.sidebar.selectbox('Área', areas_comodo, key='area')
if selecao_area !=None:
    codId_area = [record.get("id") for record in dados_comodo[0]['areas'] if record.get("nome") == selecao_area]
else:
    codId_area = [0]

dia = st.sidebar.date_input('Selecione o dia', format="DD/MM/YYYY")
data_inicio = str(dia)
data_fim = str(dia + timedelta(days=1))

if st.sidebar.button('Baixar Dados'):
    df_bruto = coleta_banco(data_inicio, data_fim)
    df_tabelao = tabelao(df_bruto['json_data'], codId_franquia[0])
    df_blocos = processar_blocos(df_tabelao)
    df_tabelao_filtro = df_tabelao[(df_tabelao['deviceId'] == codId_comodo[0]) & (df_tabelao['area'] ==  selecao_area)]
    df_blocos_filtro = df_blocos[(df_blocos['codId_residente'] == codId_residente[0]) & (df_blocos['local'] == selecao_comodo) & (df_blocos['area'] == selecao_area)]
    df_acoes = coleta_acoes(df_tabelao_filtro)
    df_acoes_classificadas = coleta_acoes_classificadas(df_tabelao_filtro)

if st.sidebar.button('Apagar Cache'):
    st.cache_data.clear()

st.sidebar.info('Versão: 4.0a')    

tab1, tab2, tab3, tab4 = st.tabs(['Gráficos', 'Dados', 'Ações', 'Json API'])

with tab1:
    try:
        st.write('**Dados Brutos**')
        grafico_dados_brutos(df_tabelao_filtro)
        st.write('**Dados Tratados**')
        grafico_grantt(df_blocos_filtro)
    except:
        st.write('Nada para mostrar')
with tab2:
    try:
        st.write('Tabelão')
        st.dataframe(df_tabelao_filtro)
        st.write('Blocos de Eventos')
        st.dataframe(df_blocos_filtro)

    except:
        st.write('Nada para mostrar')

with tab3:
    try:
        st.dataframe(df_acoes, width=1500, height=600)
        st.dataframe(df_acoes_classificadas, width=1500, height=600)
    except:
        st.write('Nada para mostrar')

with tab4:
    try:
        st.write(dados_comodo)
    except:
        st.write('Nada para mostrar')
