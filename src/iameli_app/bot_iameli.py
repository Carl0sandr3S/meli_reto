from langchain.schema  import SystemMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from langchain.chains.sequential import SequentialChain,SimpleSequentialChain
from langchain.memory import ConversationBufferMemory
from langchain.agents import initialize_agent, load_tools, AgentType
from langchain_experimental.agents.agent_toolkits import create_python_agent
from langchain_experimental.tools.python.tool import PythonREPLTool
from langchain_community.agent_toolkits import create_sql_agent
from langchain.sql_database import SQLDatabase
import json
from markdown import markdown

from langchain.prompts import (
    ChatPromptTemplate,
    PromptTemplate,
    SystemMessagePromptTemplate,
    AIMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage
)


config = {
    'user':'root',
    'password':'localdev3',
    'host':'localhost',
    'database':'ejemplo_db'
}

#agente de consulta base de datos
with open('key.txt') as f:
    key = f.read()

def consulta_db(mensaje_usuario : str, config : dict,key : str) -> str:
    llm = ChatOpenAI(openai_api_key=key,temperature=0.2) 
    coneccion = f"mysql+mysqlconnector://{config['user']}:{config['password']}@{config['host']}/{config['database']}"
    db = SQLDatabase.from_uri(coneccion)
    agent = create_sql_agent(
        llm,
        db=db,
    )
    npl_db = agent.invoke(f"{mensaje_usuario}")
    print(npl_db)

    #agente que convierte los datos provenientes de la base de datos a una estructura de datos tipo dict
    npl_diccionario = agent.invoke(f'''apartir del siguinte texto {npl_db["output"]} identifica los datos como:
                            seller id, city,total transactions, level, power y cluster. 
                            una vez los haya identificado construye un diccionario 
                                y retorna solo el diccionario 
                            con los siguintes keys:
                                                    
                            -seller_id
                            - city
                            - total_transactions
                            - level
                            - power
                            - cluster


                ''')
    print(npl_diccionario)
    diccionario_seller = npl_diccionario.get("output", {})
    if isinstance(diccionario_seller, str):
        diccionario_seller = eval(diccionario_seller)  
        diccionario_seller = {key.replace(' ', '_'): value for key, value in diccionario_seller.items()}

    mapeo_clusters = {
        0: "Cuentas Nuevas",
        1: "Sellers Intermedios",
        2: "Top Sellers"
    }
    diccionario_seller["segmento"] = mapeo_clusters.get(diccionario_seller.get("cluster"), "General" )
    return diccionario_seller

def generar_estrategia(diccionario_seller: dict, key: str, ) -> str:
    """Dado un registro de seller, genera una estrategia comercial."""
    
    
    # 3. Crea el prompt template
    template = """
    Cuando respondas, comienza presentandote como  IAMELI, un asistente experto en e-commerce.

    Descripcion de variables
    - seller_id ({seller_id}): ID único que identifica al vendedor en la plataforma.
    - city ({city}): Ciudad principal desde donde opera el seller.
    - total_transactions ({total_transactions}): Número total de transacciones históricas del seller.
    - level ({level}): Nivel de reputación del seller en la plataforma (0 = muy bajo … 5 = excelente).
    - power ({power}): Estatus de Power Seller (0 = ninguno, 1 = Bronce, 2 = Oro, 3 = Platino).
    - segmento ({segmento}): Segmento o clúster al que pertenece el seller despues de realizar un clasificador.

    Objetivo
    Con base en estas caracteristicas proporcionadas, proponga una estrategia comercial personalizada para el seller en cuestion SOLO acorde a los parametros ingresados. 
    Haciendo saber en cada momento cual es el estado del seller. La estrategia debe incluir  al menos:
      * Una campaña de cuotas o financiamiento  
      * Un incentivo (descuento, gift card, programa de fidelidad)  
      * Una mejora recomendada en catálogo o presentación de producto  

    Estructura su respuesta en secciones con encabezados y emojis llamativos.
    """
    prompt = PromptTemplate(input_variables=[
            "seller_id","city","total_transactions",
            "level","power","segmento"
        ],
        template=template
    )
    
    # 4. Instancia el LLMChain
    llm = ChatOpenAI(openai_api_key=key, model_name="gpt-4o", temperature=0.7)
    chain = LLMChain(llm=llm, prompt=prompt)
    
    # 5. Ejecuta y retorna el texto generado
    return chain.run(
        seller_id=diccionario_seller["seller_id"],
        city=diccionario_seller["city"],
        total_transactions=diccionario_seller["total_transactions"],
        level=diccionario_seller["level"],
        power=diccionario_seller["power"],
        segmento=diccionario_seller["segmento"]
    )
#datos_seller = consulta_db("dime la informacion del  seller con id  1207093176",config, key)   
#print(generar_estrategia(datos_seller, key))
#####
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def chat_ui(request: Request):
    # al cargar por primera vez no hay mensajes
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/generate", response_class=HTMLResponse)
async def chat_generate(request: Request, mensaje_usuario: str = Form(...)):

    datos_seller = consulta_db(mensaje_usuario, config, key)
    bot_message_ = generar_estrategia(datos_seller, key)


    bot_message_html = markdown(
       bot_message_,
        extensions=["extra", "sane_lists"]
    )

   
    return templates.TemplateResponse("index.html", {
        "request": request,
        "mensaje_usuario": mensaje_usuario,
        "bot_message_html": bot_message_html
    })