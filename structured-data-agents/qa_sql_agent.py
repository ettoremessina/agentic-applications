from langchain.agents import create_sql_agent
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain.agents.agent_types import AgentType
from langchain.utilities import SQLDatabase
from langchain_openai import ChatOpenAI
from langchain_community.llms import Ollama
from langchain.callbacks.tracers import ConsoleCallbackHandler
from sqlalchemy import MetaData
from sqlalchemy import Column, Integer, String, Table, Date, Float
from sqlalchemy import create_engine, insert
import pandas as pd
import argparse
from datetime import datetime

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

def prepare_database(engine):
    metadata_obj = MetaData()

    table_qc = Table(
        "QualityChecks",
        metadata_obj,
        Column("ID", Integer, primary_key=True, autoincrement=True),
        Column("Article_Code", String(20), nullable=False),
        Column("Description", String(100), nullable=False),
        Column("Category", String(50), nullable=False),
        Column("Date_of_Check", Date, nullable=False),
        Column("Quantity_in_First_Class", Integer, nullable=False),
        Column("Quantity_in_Second_Class", Integer, nullable=False),
        Column("Quantity_Rejected", Integer, nullable=False),
    )

    metadata_obj.create_all(engine)

    df = pd.read_csv("../datasets/quality_assurance.csv")
    date_format = '%Y-%m-%d'
    for record in df.itertuples():
        date_of_check = datetime.strptime(record[4], date_format)
        stmt = insert(table_qc).values(
            Article_Code=record[1],
            Description=record[2],
            Category=record[3],
            Date_of_Check=date_of_check,
            Quantity_in_First_Class=record[5],
            Quantity_in_Second_Class=record[6],
            Quantity_Rejected=record[7]
        )
        with engine.begin() as conn:
            conn.execute(stmt)
     
parser = argparse.ArgumentParser(description='Chat with an sql agent')
parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
parser.add_argument('-c', '--connector', type=str, required=False, default='openai', help='Connector to use: openai|ollama')
parser.add_argument('-m', '--model', type=str, required=False, default='gpt-4', help='Model name to use (e.g. gpt-4, gemma2, llama3.2, ...)')
args = parser.parse_args()

if args.connector == 'openai':
    model = ChatOpenAI(model=args.model, temperature=0.)
elif args.connector == 'ollama':
    ollama_url = "http://localhost:11434"
    model = Ollama(base_url=ollama_url, model=args.model, temperature=0.)
else:
    raise ValueError(f"Unsupported connector: {args.connector}. Use 'openai' or 'ollama'")

engine = create_engine("sqlite:///:memory:")
prepare_database(engine)
db = SQLDatabase(engine)

agent = create_sql_agent(
    llm=model,
    toolkit=SQLDatabaseToolkit(db=db, llm=model),
    verbose=True,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    max_iterations=50,
    handle_parsing_errors=True,
    return_intermediate_steps=True
)

config = {}
if args.verbose:
    config = config | {'callbacks': [ConsoleCallbackHandler()]}

system_msg = """QualityCheck is a table of quality control results on items that are toys.
The ID field of the QualityCheck table is the primary key, autoincrement.
Article_Code is the article code.
Description is the description of the article.
Category is the category, an enumerated value.
Date_of_Check is the date on which the quality check was done.
Quantity_in_First_Class is the number of items classified as first choice (or first class), that is, those that passed the check without defects.
Quantity_in_Second_Class is the number of items classified as second choice (or second class), i.e., those that passed inspection but with tolerable, though present, defects.
Quantity_Rejected is the number of items rejected because they had unacceptable defects.
"""

print("Chat with me (ctrl+D to quit)!\n")

while True:
    try:
        question = input("human: ")
        answer = agent.invoke(
            "system: " + system_msg 
            + '\n' 
            + "user:" + question,
            config=config
        )
        print("agent: ", answer['output'])
    except EOFError:
        print("\nGoodbye!")
        break
    except Exception as e:
        print(f"{bcolors.FAIL}{type(e)}")
        print(f"{bcolors.FAIL}{e.args}")
        print(f"{bcolors.FAIL}{e}")
