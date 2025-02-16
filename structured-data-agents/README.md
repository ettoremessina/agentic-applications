# structured-data-agents
Demo and experiments with agent applications for queries on structured data.

Dataset used is: ../datasets/quality_assurance.csv

## qa_pandas_agent.py
Agentic application that uses **langchain_experimental.agents.agent_toolkits.create_pandas_dataframe_agent** to answer questions about data in a relational database table.

### Examples of usages:
- python qa_pandas_agent.py -c openai -m gpt-4o-mini -v
- python qa_pandas_agent.py -c ollama -m gemma2


## qa_sql_agent.py
Agentic application that uses **langchain.agents.create_sql_agent** to answer questions about data in a relational database table.

### Examples of usages:
- python qa_sql_agent.py -c openai -m gpt-4o-mini -v
- python qa_sql_agent.py -c ollama -m gemma2


## Examples of questions (for both scripts):
- What is the percentage of rejected articles?
- What is the percentage of rejected articles of Educational category?
- What are the distinct categories?
- What is the worst category?
- What is the range of dates of checks?
- Are there articles specialized for kids? If they are, what are them?
- What is the total quantity for articles of the Education category?
- What is the ration between first class and 2nd class for - Education category?
- What is the most recent check for Educational category?
- How many articles of category Vehicles have defects?
