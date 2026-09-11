from langgraph.graph.state import StateGraph,START,END
from typing import Annotated,TypedDict
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage,BaseMessage
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import InMemorySaver

# build model

model = ChatOllama(model='gemma4:12b',temperature=0)

class ChatState(TypedDict):
    messages : Annotated[list[HumanMessage],add_messages]


def chat_node(state: ChatState):

    messages = state['messages']

    response =  model.invoke(messages)

    return {'messages': [response]}


checkpoint = InMemorySaver()

graph = StateGraph(ChatState)

graph.add_node('chat_node',chat_node)

graph.add_edge(START,'chat_node')
graph.add_edge('chat_node',END)


CONFIG = {'configurable': {'thread_id': 'thread_1'}}
chatbot =  graph.compile(checkpointer=checkpoint)




# if __name__ == '__main__':
#     pass
    