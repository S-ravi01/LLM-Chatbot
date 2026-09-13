import streamlit as st
from langchain_core.messages import HumanMessage
from backend import chatbot,get_threads,remove_thread_from_db
import time
import uuid


# *************************** utilit fucntions ****************************

def reset_chat():
    thread_id = generate_threadId()
    st.session_state['thread_id'] = thread_id
    add_thread(st.session_state['thread_id'])
    st.session_state['message_history'] = []

def add_thread(thread_id):
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].append(thread_id)

def generate_threadId() -> str:
    return uuid.uuid4()

def load_conversation(thread_id):
    state = chatbot.get_state(config={'configurable': {'thread_id':thread_id}})
    return state.values.get('messages',[])

def steam_reponse():

    for message_chunk,metadata in chatbot.stream(
    {'messages': [HumanMessage(content=user_input)]},
    stream_mode="messages",
    config=CONFIG):

        yield message_chunk.content 


    
# *************************** session setup ****************************

if 'message_history' not in st.session_state:
    st.session_state['message_history'] =[]

if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = str(generate_threadId())

if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads'] = get_threads()

add_thread(st.session_state['thread_id'])

# *************************** UI elements ****************************

with st.sidebar:
    st.title("LLM Chatbot")
    if st.button('New Chat', icon ="📝",icon_position='right'):
        reset_chat()
    st.title("Conversion history")

# st.sidebar.button(str(generate_threadId()))

    for thread_id in st.session_state['chat_threads'][::-1]:

        title, delete = st.columns([0.85,0.15])

        with title:
            if st.button(
                str(thread_id),
                use_container_width=True,
                width='stretch',
                wrap=False
            ):

                st.session_state['thread_id'] = thread_id

                message = load_conversation(thread_id)
                temp_msg = []

                for msg in message:
                    if isinstance(msg,HumanMessage):
                        role = 'user'
                    else:
                        role = 'ai'
                    temp_msg.append({'role' : role, 'content' : msg.content})
                st.session_state['message_history'] = temp_msg


        with delete:
            if delete.button(
                str("🗑️"),
                key=f"delete_{thread_id}",
                help='delete this chat'
                ):

                remove_thread_from_db(thread_id)

                st.session_state['chat_threads'].remove(thread_id)

                if st.session_state.get("thread_id") == thread_id:
                    st.session_state['thread_id'] == None

                st.rerun()
        

# title.button("chat title will be here",use_container_width=True,)
# if delete.button("🗑️"):
#     remove_thread("d4c5d02b-4e08-49ac-aa83-b326f72487b3")


# *************************** Main UI ****************************

for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])
        
CONFIG = {'configurable': {'thread_id':st.session_state['thread_id']}}

user_input = st.chat_input("type here..")


if user_input:

    st.session_state['message_history'].append({'role':'user','content':user_input})    
    with st.chat_message('user'):
        st.text(user_input)

    with st.chat_message('ai'):
        start_time = time.perf_counter()
        response = st.write_stream(steam_reponse())

    # response = chatbot.invoke({'messages': [HumanMessage(content=user_input)]},config=CONFIG )
    # print(response)
    # response = response['messages'][-1].content

    # total_duration_ns = response['messages'][-1].response_metadata.get('total_duration', 0)

    total_seconds = time.perf_counter() - start_time

    minutes = int(total_seconds // 60)
    seconds = total_seconds % 60

    if minutes > 0:
        duration_text = f"{minutes}m {seconds:.2f}s"
    else:
        duration_text = f"{seconds:.2f}s"

    st.write(f"⏱️ Response time: {duration_text}")
    # st.write(f"{response['messages'][-1].usage_metadata}")

    st.session_state['message_history'].append({'role':'ai','content':response})
