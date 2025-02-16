from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain_openai import ChatOpenAI
from langchain_community.llms import Ollama
from langchain.callbacks.tracers import ConsoleCallbackHandler
import pandas as pd
import argparse

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

df = pd.read_csv("../datasets/quality_assurance.csv")

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

agent = create_pandas_dataframe_agent(
    model, 
    df, 
    verbose=True if args.verbose else False, 
    agent_executor_kwargs={"handle_parsing_errors": True}, 
    allow_dangerous_code=True,
    max_iterations=50
)

config = {}
if args.verbose:
    config = config | {'callbacks': [ConsoleCallbackHandler()]}

print("Chat with me (ctrl+D to quit)!\n")

while True:
    try:
        question = input("human: ")
        answer = agent.invoke(
            question,
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