from langgraph.graph.state import StateGraph,START,END
from typing import Annotated,TypedDict
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage,BaseMessage
from langgraph.graph.message import add_messages
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3
from pathlib import Path

from langgraph.prebuilt import ToolNode,tools_condition
from langchain_core.tools import tool
from langchain_classic.tools import ddg_search
from langchain_community.tools import DuckDuckGoSearchRun


# from frontend import CONFIG


DATABASE_DIRECTORY = Path("/Users/ravisuryawanshi/VS Code/Agentic AI Projects/Stremlit Chatbot/database")
DATABASE_FILE = DATABASE_DIRECTORY / "chat_history.db"

DATABASE_DIRECTORY.mkdir(parents=True,exist_ok=True)

conn =  sqlite3.connect(DATABASE_FILE,check_same_thread=False)                  # connction object
cursor = conn.cursor()


search_tool = DuckDuckGoSearchRun()

@tool
def calculator(a : float , b : float, operation : str) -> float:

    """this function takes 2 argument numebrs and apply provided mathemactical operation on them and return the result """

    try:
        if operation == 'add':
            result =  a + b
        elif operation == 'sub':
            result = a - b
        elif operation == 'mul':
            result = a + b
        elif operation == 'div':
            if a == 0 or b == 0 :
                return {'error' : 'Divison by 0 is not allowed'}
            else:
                result = a / b
        else:
            return {'error' : 'unsupported operation'}

        return {'first_num': a , 'second_num' : b,'openration': operation, 'result': result}
    except Exception as e:
        return{'error' : str(e)}
        

tools = [calculator,search_tool]

tool_node = ToolNode(tools)

# build model
model = ChatOllama(model='gemma4:12b',temperature=0).bind_tools(tools)

class ChatState(TypedDict):
    messages : Annotated[list[HumanMessage],add_messages]

def chat_node(state: ChatState):

    messages = state['messages']

    response =  model.invoke(messages)

    return {'messages': [response]}

checkpoint = SqliteSaver(conn=conn)

graph = StateGraph(ChatState)

graph.add_node('chat_node',chat_node)
graph.add_node('tools',tool_node)

graph.add_edge(START,'chat_node')
graph.add_conditional_edges('chat_node',tools_condition)
graph.add_edge('tools','chat_node')



chatbot =  graph.compile(checkpointer=checkpoint)

# CONFIG = {'configurable': {'thread_id': 'thread_2'}}

# response = chatbot.invoke(
#     {'messages': [HumanMessage(content="search on web what is pune weather today ")]},
#     config=CONFIG)

# print(response)

threads_list = set()

def get_threads():
    for thread in checkpoint.list(None):
        threads_list.add (thread.config['configurable']['thread_id'])
    return list(threads_list)

def remove_thread_from_db(thread_id):

    if thread_id in get_threads():
        cursor.execute("DELETE FROM checkpoints WHERE thread_id = ?",(thread_id,))
        conn.commit()

# print(list(threads_list))



# if __name__ == '__main__':
#     pass
    