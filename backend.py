from langgraph.graph.state import StateGraph,START,END
from typing import Annotated,TypedDict
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage,BaseMessage
from langgraph.graph.message import add_messages
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3
from pathlib import Path
# from frontend import CONFIG


DATABASE_DIRECTORY = Path("/Users/ravisuryawanshi/VS Code/Agentic AI Projects/Stremlit Chatbot/database")
DATABASE_FILE = DATABASE_DIRECTORY / "chat_history.db"

DATABASE_DIRECTORY.mkdir(parents=True,exist_ok=True)

conn =  sqlite3.connect(DATABASE_FILE,check_same_thread=False)                  # connction object

# build model
model = ChatOllama(model='gemma4:12b',temperature=0)

class ChatState(TypedDict):
    messages : Annotated[list[HumanMessage],add_messages]

def chat_node(state: ChatState):

    messages = state['messages']

    response =  model.invoke(messages)

    return {'messages': [response]}

checkpoint = SqliteSaver(conn=conn)

graph = StateGraph(ChatState)

graph.add_node('chat_node',chat_node)

graph.add_edge(START,'chat_node')
graph.add_edge('chat_node',END)


# CONFIG = {'configurable': {'thread_id': 'thread_2'}}
chatbot =  graph.compile(checkpointer=checkpoint)

# response = chatbot.invoke(
#     {'messages': [HumanMessage(content="what is capital of belgium")]},
#     config=CONFIG)

# print(response)

threads_list = set()

def get_threads():
    for thread in checkpoint.list(None):
        threads_list.add (thread.config['configurable']['thread_id'])
    return list(threads_list)


# print(list(threads_list))



# if __name__ == '__main__':
#     pass
    