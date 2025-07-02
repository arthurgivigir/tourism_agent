import streamlit as st 
import os
from dotenv import load_dotenv

from agent import Agent
import os

# Carrega as variáveis do arquivo .env
load_dotenv()

st.set_page_config(layout="wide")
st.title("Turismo para mochileiros")
st.write("Este app te ajudará a planejar sua viagem de forma inteligente e econômica, utilizando inteligência artificial para otimizar seu roteiro.")

# Usa a chave do arquivo .env
openai_key = os.getenv("OPENAI_API_KEY")
agent = Agent(openai_key)

container = st.container()
with container :
    request = st.text_area("Descreva seu roteiro de viagem", placeholder="Exemplo: Quero visitar Paris e Londres em 5 dias, começando por Paris. Prefiro transporte público e gostaria de visitar museus e parques.", height=200)   
    button = st.button("Planejar viagem")

    box = st.container(height=300)
    with box:
        container = st.empty()
        container.write("Sugestões de itinerário aparecerão aqui após o planejamento.")
    
    if button and request:
        with st.spinner("Planejando sua viagem..."):
            itinerary = agent.get_tips(request)
            container.write(itinerary["itinerary"])
            st.success("Itinerário planejado com sucesso!")
