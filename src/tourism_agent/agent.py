from langchain.llms import OpenAI

from langchain.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate
)

from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain, SequentialChain

import logging
import time

logging.basicConfig(level=logging.DEBUG)


class TravelTemplate:
    def __init__(self):
        self.system_template = """
        You are a travel assistant specialized in low-cost, minimalist adventures for backpackers.

        The user’s request will be marked with four hashtags. Step by step, interpret their preferences, timeframe, and budget, and transform their request into a practical, budget-friendly itinerary.

        Start by reasoning through affordable routes, free or low-cost attractions, and simple accommodations (like hostels or camping spots). Always prioritize experiences that are accessible on foot, by bus, or local transportation.

        Build a bulleted list showing:
            •	Clear start and end points (with specific addresses when possible)
            •	The type of transport between each location
            •	Activities that are either free or low-cost
            •	Tips to save money along the way (if relevant)
            •   Any necessary precautions or considerations for safety and comfort
            •   Which bus or metro lines to take, if applicable

        If the user doesn’t specify a starting location, assume a logical one and provide a concrete address. The goal is to create an enjoyable and achievable plan with simplicity and spontaneity in mind.

        Return only the list with no extra commentary.

        Answer the user in portuguese, using a friendly and engaging tone.
        """

        self.human_template = """
        #### {request}
        """
        self.system_message_prompt = SystemMessagePromptTemplate.from_template(self.system_template)
        self.human_message_prompt = HumanMessagePromptTemplate.from_template(self.human_template)
        self.chat_prompt = ChatPromptTemplate.from_messages([self.system_message_prompt,
                                                             self.human_message_prompt])
        
        
class MappingTemplate:
    def __init__(self):
        self.system_template = """
            You are an assistant designed to help backpackers and low-budget travelers
            convert simple travel plans into geolocation data.

            The input will be an itinerary marked by four hashtags. 
            Reason through each location based on affordability, accessibility (on foot, public transit), and overall simplicity, 
            and then convert it into a list of dictionaries with the **latitude**, **longitude**, **address**, and **name** of each point of interest.

            Focus on low-cost or free experiences, hostels, local food spots, public landmarks, parks, or cultural centers. 
            Use logical and walkable sequences where possible.

            Return a clean **JSON object only** (no markdown).

            For example:

            ####
            Backpacker plan: 2 days in Lisbon with little money.
            - Day 1:
                - Start at Rossio Square (Praça Dom Pedro IV, 1100-200 Lisboa, Portugal)
                - Visit Carmo Convent ruins (Largo do Carmo, 1200-092 Lisboa, Portugal)
                - Walk through Bairro Alto and enjoy street music
                - Sunset view at Miradouro de São Pedro de Alcântara (R. de São Pedro de Alcântara, 1250-237 Lisboa, Portugal)
            - Day 2:
                - Start at LX Factory (R. Rodrigues de Faria 103, 1300-501 Lisboa, Portugal)
                - Explore Belém Tower surroundings (Av. Brasília, 1400-038 Lisboa, Portugal)
                - Chill at Jardim da Estrela (Praça da Estrela, 1200-667 Lisboa, Portugal)
                - End at Time Out Market (Av. 24 de Julho 49, 1200-479 Lisboa, Portugal)
            ####

            Output:
            {{
                "days": [
                    {{
                        "day": 1,
                        "locations": [
                            {{"lat": 38.7149, "lon": -9.1409, "address": "Praça Dom Pedro IV, 1100-200 Lisboa, Portugal", "name": "Rossio Square"}},
                            {{"lat": 38.7139, "lon": -9.1416, "address": "Largo do Carmo, 1200-092 Lisboa, Portugal", "name": "Carmo Convent"}},
                            {{"lat": 38.7133, "lon": -9.1441, "address": "Bairro Alto, Lisboa, Portugal", "name": "Bairro Alto (street walk)"}},
                            {{"lat": 38.7153, "lon": -9.1445, "address": "R. de São Pedro de Alcântara, 1250-237 Lisboa, Portugal", "name": "Miradouro de São Pedro de Alcântara"}}
                        ]
                    }},
                    {{
                        "day": 2,
                        "locations": [
                            {{"lat": 38.7032, "lon": -9.1781, "address": "R. Rodrigues de Faria 103, 1300-501 Lisboa, Portugal", "name": "LX Factory"}},
                            {{"lat": 38.6916, "lon": -9.2160, "address": "Av. Brasília, 1400-038 Lisboa, Portugal", "name": "Belém Tower"}},
                            {{"lat": 38.7163, "lon": -9.1600, "address": "Praça da Estrela, 1200-667 Lisboa, Portugal", "name": "Jardim da Estrela"}},
                            {{"lat": 38.7076, "lon": -9.1484, "address": "Av. 24 de Julho 49, 1200-479 Lisboa, Portugal", "name": "Time Out Market"}}
                        ]
                    }}
                ]
            }}
            """
        self.human_template = """
        #### {itinerary}
        """
        self.system_message_prompt = SystemMessagePromptTemplate.from_template(self.system_template)
        self.human_message_prompt = HumanMessagePromptTemplate.from_template(self.human_template)
        self.chat_prompt = ChatPromptTemplate.from_messages([self.system_message_prompt,
                                                             self.human_message_prompt])
        
class Agent:
    def __init__(self, open_ai_key, model="gpt-3.5-turbo", temperature=0.1):
        self.open_ai_key = open_ai_key
        self.model = model
        self.temperature = temperature
        self.logger = logging.getLogger(__name__)
        self.chat_model = ChatOpenAI(model=self.model,
                         temperature=self.temperature,
                         openai_api_key=self.open_ai_key,
                         openai_organization="org-RFtOelfLtrbxfp1wU2xF2Nml")

    def get_tips(self, request):
        travel_prompt = TravelTemplate()
        
        parser = LLMChain(
            llm=self.chat_model,
            prompt=travel_prompt.chat_prompt,
            output_key="itinerary"
        )

        chain = SequentialChain(
            chains=[parser],
            input_variables=["request"],
            output_variables=["itinerary"],
            verbose=True
        )
        return chain(
            {"request": request},
            return_only_outputs=True
        )