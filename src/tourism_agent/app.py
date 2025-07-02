import streamlit as st 

from agent import Agent

st.set_page_config(layout="wide")
st.title("Turismo para mochileiros")
st.write("Este app te ajudará a planejar sua viagem de forma inteligente e econômica, utilizando inteligência artificial para otimizar seu roteiro.")

agent = Agent("")

col1, col2 = st.columns(2)

with col1:
    request = st.text_area("Descreva seu roteiro de viagem", placeholder="Exemplo: Quero visitar Paris e Londres em 5 dias, começando por Paris. Prefiro transporte público e gostaria de visitar museus e parques.", height=200)   
    button = st.button("Planejar viagem")

    box = st.container(height=300)
    with box:
            container = st.empty()
            container.write("Sugestões de itinerário aparecerão aqui após o planejamento.")
    
    if button and request:
        with st.spinner("Planejando sua viagem..."):
            itinerary = agent.get_tips(request)
            container.write(itinerary["travel_tips"])
            st.success("Itinerário planejado com sucesso!")


with col2:
    st.write("Dicas de viagem:")