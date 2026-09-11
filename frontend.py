import streamlit as st
from langchain_core.messages import HumanMessage
from backend import chatbot


if 'message_history' not in st.session_state:
    st.session_state['message_history'] =[]


for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])
        
CONFIG = {'configurable': {'thread_id': 'thread_1'}}

user_input = st.chat_input("type here..")


if user_input:

    st.session_state['message_history'].append({'role':'user','content':user_input})    
    with st.chat_message('user'):
        st.text(user_input)

    response = chatbot.invoke({'messages': [HumanMessage(content=user_input)]},config=CONFIG )

    print(response)

    total_duration_ns = response['messages'][-1].response_metadata.get('total_duration', 0)

    total_seconds = total_duration_ns / 1_000_000_000

    minutes = int(total_seconds // 60)
    seconds = total_seconds % 60

    if minutes > 0:
        duration_text = f"{minutes}m {seconds:.2f}s"
    else:
        duration_text = f"{seconds:.2f}s"


    st.write(f"⏱️ Response time: {duration_text}")
    st.write(f"{response['messages'][-1].usage_metadata}")

    response = response['messages'][-1].content

    st.session_state['message_history'].append({'role':'ai','content':response})
    with st.chat_message('ai'):
        st.text(response)
