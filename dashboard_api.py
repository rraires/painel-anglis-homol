import streamlit as st
import requests
# from pandas.io.json import json_normalize
import pandas as pd
import json
import time
import cv2

st.set_page_config(layout='wide')

st.sidebar.image('logo_anglis-bg.png',width=200 )
col1, col2, col3 = st.columns([2,1,1])
# col1.image('logo_anglis-bg.png',width=200 )
col1.header('Painel de Monitoração')
st.write("---")
# col3.image('logo_elissa.png', width=120)


#API de Status Novo

url = 'http://app.anglis.com.br:8081/tudo'
response = requests.get(url)
data = response.json()
selecao = st.sidebar.selectbox('Cliente',data.keys())
# selecao = 'Joaquim Aires Martins'
dict_cliente = data[selecao]['data']
lista_comodos = dict_cliente.keys()
col3.header(selecao)

# st.write(data[selecao])
# st.write(dado)

# for key in data[selecao].keys():
#     if data[selecao][key] == None:
#         st.write(key,' - OFFLINE')
#     elif (data[selecao][key] != None) and (data[selecao][key]['last_keepalive'] <= 40):
#         st.write(key,' - ONLINE - Último Keepalive: ', data[selecao][key]['last_keepalive'])
#     else:
#         st.write(key,' - OFFLINE - Último Keepalive: ', data[selecao][key]['last_keepalive'])


# Colunas para mostrar as informações de cada quarto
col1, col2, col3, col4 = st.columns(4)


# Loop pelos comodos
for i, comodo in enumerate(lista_comodos):
    # Selecionar a coluna para mostrar as informações
    if i % 4 == 0:
        col = col1
    elif i % 4 == 1:
        col = col2
    elif i % 4 == 2:
        col = col3
    else:
        col = col4
    
    # Capturar dados do comodo
    
    if "last_keepalive" in dict_cliente[comodo]:
        queda = int(dict_cliente[comodo]['people_status'])
        presenca = int(dict_cliente[comodo]['num_people'])
        movimento = int(dict_cliente[comodo]['vel'])
        if (queda != 2) and (presenca == -1) and (movimento >= 2):
            status = "Pessoa em Movimento"
            card = './icones/bold_movimento_verde.png'
        elif (queda != 2) and (presenca == -1) and (movimento <= 1):
            status = "Pessoa Parada"
            card = './icones/bold_parado_verde.png'
        elif (queda != 2) and (presenca == 0):
            status = "Ninguém no Cômodo"
            card = './icones/bold_fora_quarto_verde.png'
        elif (queda == 2):
            status = "Queda!"
            card = './icones/bold_queda.png'
        elif (movimento == 0):
            status = "Ninguém no Cômodo"
            card = './icones/bold_fora_quarto_verde.png'
    else:
        card = './icones/bold_offline.png'
        
    # Mostrar as informações do quarto
    with col:
        card = cv2.imread(card)
        cv2.putText(img = card, text = f"{comodo}", org = (30, 50), fontFace = cv2.FONT_HERSHEY_DUPLEX,
                    fontScale = 1.0, color = (0, 0, 0), thickness = 2)
        card = cv2.cvtColor(card, cv2.COLOR_BGR2RGB)
        
        col.image(card)