import streamlit as st
import json
import paho.mqtt.client as mqtt
import time


st.set_page_config(page_title="Dashboard de ocupação", layout="wide")


st.sidebar.image('jumperfour_logo.png')
st.header("Painel Ocupação de Posições de Trabalho")


######################## MQTT #############################

# Variável global para armazenar a mensagem JSON
current_message = None

# Função chamada quando a conexão com o broker é estabelecida
def on_connect(client, userdata, flags, rc):
    print(f"Conectado com o código {rc}")
    # Subscrever ao tópico desejado
    client.subscribe("jumperfour2")

# Função chamada quando uma mensagem é recebida
def on_message(client, userdata, msg):
    global current_message
    try:
        # Decodificar a mensagem JSON
        current_message = json.loads(msg.payload.decode('utf-8'))
    except json.JSONDecodeError as e:
        print(f"Erro ao decodificar JSON: {e}")

# Criar um cliente MQTT
client = mqtt.Client()

# Atribuir funções de callback
client.on_connect = on_connect
client.on_message = on_message

# Conectar ao broker MQTT
client.connect("pido.me", 1883, 60)

# Iniciar loop para processar callbacks e reconectar automaticamente
client.loop_start()

#############################################################


tab1, tab2 = st.tabs(["Sala A", "Sala B"])


with tab1:
    st.write("**Ocupação em tempo real**")

    col1, col2, col3, col4, col5, col6 = st.columns(6)

    with col1:
        card1 = st.empty()
    with col2:
        card2 = st.empty()
    with col3:
        card3 = st.empty()
    with col4:
        card4 = st.empty()
    with col5:
        card5 = st.empty()
    with col6:
        card6 = st.empty()

    linha1 = st.empty()

    col7, col8, col9, col10, col11, col12 = st.columns(6)
    with col7:
        card7 = st.empty()
    with col8:
        card8 = st.empty()
    with col9:
        card9 = st.empty()
    with col10:
        card10 = st.empty()
    with col11:
        card11 = st.empty()
    with col12:
        card12 = st.empty()
    linha2= st.empty()
    info1 = st.empty()

try:
    while True:
        if current_message != None:

            if current_message['Sala1'][0]['1']:
                pos1 = 'ocupado.png'
            else:
                pos1 = 'vazio.png'
            if current_message['Sala1'][0]['2']:
                pos2 = 'ocupado.png'
            else:
                pos2 = 'vazio.png'
            if current_message['Sala1'][0]['3']:
                pos3 = 'ocupado.png'
            else:
                pos3 = 'vazio.png'
            if current_message['Sala1'][0]['4']:
                pos4 = 'ocupado.png'
            else:
                pos4 = 'vazio.png'
            if current_message['Sala1'][0]['5']:
                pos5 = 'ocupado.png'
            else:
                pos5 = 'vazio.png'
            if current_message['Sala1'][0]['6']:
                pos6 = 'ocupado.png'
            else:
                pos6 = 'vazio.png'
            if current_message['Sala1'][0]['7']:
                pos7 = 'ocupado.png'
            else:
                pos7 = 'vazio.png'
            if current_message['Sala1'][0]['8']:
                pos8 = 'ocupado.png'
            else:
                pos8 = 'vazio.png'
            if current_message['Sala1'][0]['9']:
                pos9 = 'ocupado.png'
            else:
                pos9 = 'vazio.png'
            if current_message['Sala1'][0]['10']:
                pos10 = 'ocupado.png'
            else:
                pos10 = 'vazio.png'
            if current_message['Sala1'][0]['11']:
                pos11 = 'ocupado.png'
            else:
                pos11 = 'vazio.png'
            if current_message['Sala1'][0]['12']:
                pos12 = 'ocupado.png'
            else:
                pos12 = 'vazio.png'

            with card1:
                with st.container():
                    st.write('**Posição 1**')
                    st.image(pos1, width=60)
            with card2:
                with st.container():
                    st.write('**Posição 2**')
                    st.image(pos2, width=60)
            with card3:
                with st.container():
                    st.write('**Posição 3**')
                    st.image(pos3, width=60)
            with card4:
                with st.container():
                    st.write('**Posição 4**')
                    st.image(pos4, width=60)
            with card5:
                with st.container():
                    st.write('**Posição 5**')
                    st.image(pos5, width=60)
            with card6:
                with st.container():
                    st.write('**Posição 6**')
                    st.image(pos6, width=60)
            with linha1:
                st.divider()
            with card7:
                with st.container():
                    st.write('**Posição 7**')
                    st.image(pos7, width=60)
            with card8:
                with st.container():
                    st.write('**Posição 8**')
                    st.image(pos8, width=60)
            with card9:
                with st.container():
                    st.write('**Posição 9**')
                    st.image(pos9, width=60)
            with card10:
                with st.container():
                    st.write('**Posição 10**')
                    st.image(pos10, width=60)
            with card11:
                with st.container():
                    st.write('**Posição 11**')
                    st.image(pos11, width=60)
            with card12:
                with st.container():
                    st.write('**Posição 12**')
                    st.image(pos12, width=60)
            with linha2:
                st.divider()
            with info1:
                with st.container():
                    ocupadas = 0
                    vazias = 0

                    for key, value in current_message['Sala1'][0].items():
                        if value == True:
                            ocupadas += 1
                        else:
                            vazias += 1

                    taxa_ocupacao = ocupadas/len(current_message['Sala1'][0])
                    st.metric('Taxa de Ocupação', value=f"{taxa_ocupacao:.0%}")
        time.sleep(5)
        pass
except KeyboardInterrupt:
    print("Encerrando...")
    client.loop_stop()
    client.disconnect()