from langchain_community.utilities import SQLDatabase
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
import re

load_dotenv()
sql_uri = f"postgresql+psycopg2://{os.getenv('DBUSER')}:{os.getenv('DBPASS')}@{os.getenv('DBHOST')}:{os.getenv('DBPORT')}/{os.getenv('DBSCHEMA')}"
db = SQLDatabase.from_uri(sql_uri)

def get_schema(_):
    return db.get_table_info(table_names=["userdata"])

def extract_query(query):
    sql_code_match = re.search(r"```sql(.*?)```", query, re.DOTALL)
    print(sql_code_match)
    if sql_code_match:
        sql_code = sql_code_match.group(1).strip()
    else:
        sql_code = query
    return sql_code

def operator_sql_agent():
    sql_template = """
    Based on the table schema below, write a PostgreSQL query that would serve the user's request. Return only the query without any explanation:
    {schema}
    
    Question: {question}
    SQL Query:
    """
    sql_prompt = ChatPromptTemplate.from_template(sql_template)

    llm = ChatOpenAI(model="gpt-4-turbo", temperature=1)
    sql_chain = (
        RunnablePassthrough.assign(schema = get_schema)
        | sql_prompt
        | llm.bind(stop="\nSQL Result:")
        | StrOutputParser()
    )
    return sql_chain

def run_query(query):
    try:
        return db.run(query)
    except Exception as e:
        return e

def operator_agent(question: str):
    qna_template = """
    Based on the schema below, question, PostgreSQL query, and PostgreSQL response, write a natural language response.
    Respond in a structured format such as JSON if successfull operation/request. The structured response when successfull should indicate what action is requested such as insert, update, or delete, as well as what key and value are 
    involved, and status and message. If the response from the database says updated/deleted record is 0, then only inform that the key doesn't exists.:
    {schema}

    Question: {question}
    SQL Query: {query}
    SQL Response: {response}
    """
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=1)
    qna_prompt = ChatPromptTemplate.from_template(qna_template)
    sql_chain = operator_sql_agent()
    qna_chain = (
        RunnablePassthrough.assign(query = sql_chain).assign(
            schema = get_schema,
            response = lambda variables: run_query(extract_query(variables["query"]))
        )
        | qna_prompt
        | llm
        | StrOutputParser()
    )
    response = qna_chain.invoke({"question": question})
    return response






    

