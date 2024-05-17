import streamlit as st


st.set_page_config(page_title="Dashboard de ocupação", layout="wide")


st.sidebar.image('jumperfour_logo.png')
st.header("Painel Ocupação de Posições de Trabalho")

tab1, tab2 = st.tabs(["Sala A", "Sala B"])

with tab1:
    st.write("**Ocupação em tempo real**")
    col1, col2, col3, col4, col5, col6 = st.columns(6)

    with col1:
        st.write('**Posição 1**')
        st.image('ocupado.png', width=60)
    with col2:
        st.write('**Posição 2**')
        st.image('vazio.png', width=60)
    with col3:
        st.write('**Posição 3**')
        st.image('ocupado.png', width=60)
    with col4:
        st.write('**Posição 4**')
        st.image('ocupado.png', width=60)
    with col5:
        st.write('**Posição 5**')
        st.image('vazio.png', width=60)
    with col6:
        st.write('**Posição 6**')
        st.image('vazio.png', width=60)
    st.divider()
    col1, col2, col3, col4, col5, col6 = st.columns(6)

    with col1:
        st.write('**Posição 7**')
        st.image('vazio.png', width=60)
    with col2:
        st.write('**Posição 8**')
        st.image('vazio.png', width=60)
    with col3:
        st.write('**Posição 9**')
        st.image('ocupado.png', width=60)
    with col4:
        st.write('**Posição 10**')
        st.image('vazio.png', width=60)
    with col5:
        st.write('**Posição 11**')
        st.image('vazio.png', width=60)
    with col6:
        st.write('**Posição 12**')
        st.image('ocupado.png', width=60)

    st.divider()

    st.subheader("Taxa de Ocupação: 40%")



with tab2:
    st.write("**Ocupação em tempo real**")
    col1, col2, col3, col4, col5, col6 = st.columns(6)

    with col1:
        st.write('**Posição 1**')
        st.image('vazio.png', width=60)
    with col2:
        st.write('**Posição 2**')
        st.image('vazio.png', width=60)
    with col3:
        st.write('**Posição 3**')
        st.image('vazio.png', width=60)
    with col4:
        st.write('**Posição 4**')
        st.image('vazio.png', width=60)
    with col5:
        st.write('**Posição 5**')
        st.image('vazio.png', width=60)
    with col6:
        st.write('**Posição 6**')
        st.image('vazio.png', width=60)
    st.divider()
    col1, col2, col3, col4, col5, col6 = st.columns(6)

    with col1:
        st.write('**Posição 7**')
        st.image('ocupado.png', width=60)
    with col2:
        st.write('**Posição 8**')
        st.image('ocupado.png', width=60)
    with col3:
        st.write('**Posição 9**')
        st.image('vazio.png', width=60)
    with col4:
        st.write('**Posição 10**')
        st.image('vazio.png', width=60)
    with col5:
        st.write('**Posição 11**')
        st.image('vazio.png', width=60)
    with col6:
        st.write('**Posição 12**')
        st.image('ocupado.png', width=60)

    st.divider()

    st.subheader("Taxa de Ocupação: 25%")