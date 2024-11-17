from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.callbacks import StdOutCallbackHandler
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.memory.buffer import ConversationBufferMemory
from langchain_openai import ChatOpenAI
from langchain_core.tools import Tool
from operatorai import operator_agent
from fastapi import FastAPI, Request
from langchain_core.runnables import RunnableConfig
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

tools = [
    Tool(
        name="Operator",
        func=operator_agent,  
        description="Useful for answering any questions. Do not modify any question.",
    ),
]

async def agent_executor(question: str):
    llm = ChatOpenAI(model="gpt-4-turbo", temperature=1)
    prompt_template = """You are a Chat Bot called QueryBuddy that is useful for managing and maintaining database.
    Use the tool for generating and running PostgreSQL queries. Do not assume values or parameters. If something is not clear then ask the user.
    If the user says key it's primary key column and value is the data column. Note that there's only one table called userdata with 4 columns. Send it to the tool as is.
    Respond in a structured format such as JSON if successfull operation/request. The structured response when successfull should indicate what action is requested such as insert, update, or delete, as well as what key and value are 
    involved, and status and message.
    Question: {input}
    """

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", prompt_template),
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )

    agent = create_openai_functions_agent(
        llm=llm,
        tools=tools,
        prompt=prompt
    )

    conversation_memory = ConversationBufferMemory(memory_key="chat_history",
                                                input_key="input",
                                                output_key="output",
                                                return_messages=True,
                                            )

    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        return_intermediate_steps=True,
        verbose=True,
        memory=conversation_memory)

    async for chunk in agent_executor.astream({"input": question}, config=RunnableConfig(callbacks=[StdOutCallbackHandler()])):
        if "actions" in chunk:
            for action in chunk["actions"]:
                print(f"Calling Tool: `{action.tool}` with input `{action.tool_input}`")
        # Observation
        elif "steps" in chunk:
            for step in chunk["steps"]:
                    print(f"Tool Result: `{step.observation}`")
        # Final result
        elif "output" in chunk:
            print(f'Final Output: {chunk["output"]}')
            output = chunk["output"]
            return output
        else:
            raise ValueError()
        print("---")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_methods=["*"],  
    allow_headers=["*"],
)

@app.post("/ask")
async def ask_question(request: Request):
    body = await request.json()
    question = body.get("question")
    result = await agent_executor(question)
    return {"answer": result}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
