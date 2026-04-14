import os
from typing import TypedDict, Annotated, Sequence

from langchain_core.messages import BaseMessage
from langchain_openai import ChatOpenAI
from langgraph.constants import START, END
from langgraph.graph import add_messages, StateGraph


class ChatGraph:
    @staticmethod
    def create_app():
        llm = ChatOpenAI(
            model='deepseek-chat',  # 👈 必须严格使用官方指定的名称
            api_key=os.getenv('API_KEY'),  # 💡 建议使用 api_key 代替 openai_api_key (新版 LangChain 标准)
            base_url=os.getenv('API_BASE'),  # 💡 建议使用 base_url 代替 openai_api_base
            streaming=True,
            model_kwargs={
                "stream_options": {
                    "include_usage": True,  # 输出token消耗数量
                }
            }
        )

        class AgentState(TypedDict):
            messages: Annotated[Sequence[BaseMessage], add_messages]

        def model_call(state: AgentState) -> AgentState:
            res = llm.invoke(state['messages'])
            return {'messages': [res]}

        graph = StateGraph(AgentState)
        graph.add_node('agent', model_call)

        graph.add_edge(START, 'agent')
        graph.add_edge('agent', END)

        return graph.compile()
