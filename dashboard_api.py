import streamlit as st
import requests
# from pandas.io.json import json_normalize
import pandas as pd
import json
import time
import cv2

st.set_page_config(layout='wide')

st.sidebar.image('logo_anglis-bg.png',width=200 )
col1, col2, col3 = st.columns([2,1,2])
# col1.image('logo_anglis-bg.png',width=200 )
col1.header('Painel de Monitoração')
st.write("---")
# col3.image('logo_elissa.png', width=120)


# API de Status Novo

@st.cache_data
def api_codigos_clientes():
    url = 'http://app.anglis.com.br:8081/tudo'
    response = requests.get(url)
    data = response.json()
    dict_lista_clientes = {}
    for cod_cliente in data.keys():
        dict_lista_clientes[data[cod_cliente]['residente']] = int(cod_cliente) 
    return dict_lista_clientes


def api_dados(cod_cliente):
    url = f'http://app.anglis.com.br:8081/{cod_cliente}'
    response = requests.get(url)
    data = response.json()
    return data

# dict_lista_clientes = api_codigos_clientes()
# selecao = st.sidebar.selectbox('Cliente',dict_lista_clientes.keys())
# col3.subheader(selecao)
# # # # selecao = 'Joaquim Aires Martins'
# cod_cliente = dict_lista_clientes[selecao] 

# st.sidebar.button('Atualizar')

rawdata = st.sidebar.checkbox('Raw Data')


col1, col2, col3, col4, col5 = st.columns(5)

dict_lista_clientes = {"Eric Casa Teste":52825284, "Roberto Martins":94852179, "Inovabra":56081094 }

while True:
    for i, cliente in enumerate(dict_lista_clientes.keys()):
        dict_cliente = api_dados(dict_lista_clientes[cliente])
        if dict_cliente['alarme_id'] == 0:
            card = './icones/bold_fora_quarto_verde.png'
        elif dict_cliente['alarme_id'] == 3:
            card = './icones/bold_fora_cama_amarelo_parado.png'
        elif dict_cliente['alarme_id'] == 4:
            card = './icones/bold_fora_cama_amarelo_mov.png'
        elif dict_cliente['alarme_id'] == 5:
            card = './icones/bold_banheiro_verde_parado.png'
        elif dict_cliente['alarme_id'] == 6:
            card = './icones/bold_banheiro_verde_mov.png'
        elif dict_cliente['alarme_id'] == 7:
            card = './icones/bold_pessoas_verde.png'
        elif dict_cliente['alarme_id'] == 8 or dict_cliente['alarme_id'] == 9:
            card = './icones/bold_queda.png'
        else:
            card = './icones/bold_offline_1.png'
            
        # match dict_cliente['alarme_id']:
        #     case 0:
        #         card = './icones/bold_fora_quarto_verde.png'
        #     case 3:
        #         card = './icones/bold_fora_cama_amarelo_parado.png'
        #     case 4:
        #         card = './icones/bold_fora_cama_amarelo_mov.png'
        #     case 5:
        #         card = './icones/bold_banheiro_verde_parado.png'
        #     case 6:
        #         card = './icones/bold_banheiro_verde_mov.png'
        #     case 7:
        #         card = './icones/bold_pessoas_verde.png'
        #     case 8 | 9:
        #         card = './icones/bold_queda.png'
        #     case _:
        #         card = './icones/bold_offline_1.png'


        if i % 3 == 0:
            col = col1
        elif i % 3 == 1:
            col = col2
        else:
            col = col3
        with col:
            card = cv2.imread(card)
            cv2.putText(img = card, text = f"{cliente}", org = (30, 50), fontFace = cv2.FONT_HERSHEY_DUPLEX,
                        fontScale = 1.0, color = (0, 0, 0), thickness = 2)
            card = cv2.cvtColor(card, cv2.COLOR_BGR2RGB)
            st.image(card, width=400)
            if rawdata:
                st.write(dict_cliente)
    time.sleep(3)
    st.rerun()
    



# while True:

#     dict_cliente = api_dados(cod_cliente)

#     if rawdata:
#         st.sidebar.write(dict_cliente)


#     match dict_cliente['alarme_id']:
#         case 0:
#             card = './icones/bold_fora_quarto_verde.png'
#         case 3:
#             card = './icones/bold_fora_cama_amarelo_parado.png'
#         case 4:
#             card = './icones/bold_fora_cama_amarelo_mov.png'
#         case 5:
#             card = './icones/bold_banheiro_verde_parado.png'
#         case 6:
#             card = './icones/bold_banheiro_verde_mov.png'
#         case 7:
#             card = './icones/bold_pessoas_verde.png'
#         case 8 | 9:
#             card = './icones/bold_queda.png'
#         case _:
#             card = './icones/bold_offline_1.png'

#     card = cv2.imread(card)
#     cv2.putText(img = card, text = f"{selecao}", org = (30, 50), fontFace = cv2.FONT_HERSHEY_DUPLEX,
#                 fontScale = 1.0, color = (0, 0, 0), thickness = 2)
#     card = cv2.cvtColor(card, cv2.COLOR_BGR2RGB)
#     st.image(card)

#     time.sleep(5)
#     st.rerun()





################### Código Antigo ########################


# dict_cliente = data[str(cod_cliente)]['data']

# dict_lista_comodos = {}
# for cod_comodo in dict_cliente.keys():
#     dict_lista_comodos[dict_cliente[cod_comodo]['comodo']] = int(cod_comodo)

# if rawdata:
#     st.sidebar.write(dict_cliente)
    

# # Colunas para mostrar as informações de cada quarto
# col1, col2, col3, col4 = st.columns(4)


# # Loop pelos comodos
# for i, comodo in enumerate(dict_lista_comodos.keys()):
#     # Selecionar a coluna para mostrar as informações
#     if i % 4 == 0:
#         col = col1
#     elif i % 4 == 1:
#         col = col2
#     elif i % 4 == 2:
#         col = col3
#     else:
#         col = col4
    
#     # Capturar dados do comodo
    
#     if "last_keepalive" in dict_cliente[str(dict_lista_comodos[str(comodo)])]:
#         people_status = int(dict_cliente[str(dict_lista_comodos[str(comodo)])]['people_status'])
#         try:
#             num_people = dict_cliente[str(dict_lista_comodos[str(comodo)])]['num_people']
#         except:
#             num_people = 0
#         vel = dict_cliente[str(dict_lista_comodos[str(comodo)])]['vel'][0] ####### Arrumar para ver as varias velocidades de todas pessoas
#         last_keepalive = int(dict_cliente[str(dict_lista_comodos[str(comodo)])]['last_keepalive'])
#         if (last_keepalive > 40):
#             status = "Sensor OffLine"
#             card = './icones/bold_offline_1.png'

#         ###Lógica nova    
#         elif (people_status != 2) and (vel >= 2):
#             status = "Pessoa em Movimento"
#             card = './icones/bold_movimento_verde.png'
#         elif (people_status != 2) and (num_people != 0) and (vel <= 1):
#             status = "Pessoa Parada"
#             card = './icones/bold_parado_verde.png'
#         elif (people_status != 2) and (num_people == 0):
#             status = "Ninguém no Cômodo"
#             card = './icones/bold_fora_quarto_verde.png'
#         elif (people_status == 2):
#             status = "Queda!"
#             card = './icones/bold_queda.png'
            
#     else:
#         status = "Sensor OffLine"
#         card = './icones/bold_offline_1.png'
        
#     # Mostrar as informações do quarto
#     with col:
#         card = cv2.imread(card)
#         cv2.putText(img = card, text = f"{comodo}", org = (30, 50), fontFace = cv2.FONT_HERSHEY_DUPLEX,
#                     fontScale = 1.0, color = (0, 0, 0), thickness = 2)
#         card = cv2.cvtColor(card, cv2.COLOR_BGR2RGB)
        
#         col.image(card)
# time.sleep(3)
# st.rerun()


