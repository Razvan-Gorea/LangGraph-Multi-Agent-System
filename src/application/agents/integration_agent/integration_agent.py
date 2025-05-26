from application.dbutils import DbUtils
from application.environment import Environment
from application.connectors.connector_builder import ConnectorBuilder

from application.agents.extras import IntegrationState, GraphCallback
from application.agents.tools.query_connectors import create_connector_tool
from application.agents.tools.upsert_dbutils import create_upserter_tool
from application.agents.tools.list_ids_tool import list_namespace_ids_tool
from application.agents.integration_agent.pinecone_schema import PineconeSchemaHolder

from langgraph.prebuilt import create_react_agent
from langgraph.graph import START, END, StateGraph
from langgraph.types import Command
from langchain_core.messages import HumanMessage
from langchain_mistralai import ChatMistralAI
from typing import Any

class IntegrationAgent:
    # the graph is invoked telling us what stores to pull data from
    # the query node gets all the data from each node, one at a time
    # the formatter node gets data from the query node, and formats it according to the schema
    # the upserter takes the formatted data and upserts to pinecone 

    def __init__(self, env: Environment, dbutils: DbUtils, connector_builder: ConnectorBuilder):
        self.connector_builder = connector_builder
        self.dbutils = dbutils
        self.callbacks = [GraphCallback()]

        self.llm = ChatMistralAI(
            model="mistral-large-latest",
            temperature=0,
            max_retries=2,
            max_tokens=1500,
            api_key=env.DEEPSEEK_API_KEY,
            callbacks=self.callbacks
        )
 
        self.query_prompt = f'''Your job is to extract data from a data source. 
            The type of the connector is important. The type is told to you in the user message.
            Use the right tool based on the type of the connector
            Try to get all the data relevant to the body given to you.
            Do not include desciptions of endpoints, only give back what the tool calls tell you.
            When you are done, try and collect all the data you got from your tool calls and put it in your final answer, 
            without changing the data.
            Do not add any of your own text to this data, leave it as is.
            The schema of the connector is told to you in the user query.
            In your answer, include where you got the information from, e.g. the table or endpoint.
            The answer should be like this format: Content: (the data you got), Source: (wherever you got it from).
        '''
        self.formatter_prompt = f'''
            Your job is to take the data and format it according to my pinecone schema. 
            Format all of the data available to you, and your answer should be that data formatted, as a sentence in the form of a simple fact. 
            The text field in the schema should contain all of the data in that item.
            Do NOT format the first message in the state, only format the LAST message.
            The id is an important field. It should be the Source, given to you by the previous agent, followed by a number.
            Use your tool to see if there are any ids that are in use in that source. Try not to overwrite ids.
        '''
        self.upserter_prompt = f'''
            Your job is to take the formatted data, and upsert it to the pinecone database.
            Use your tool to upsert it to pinecone.
            Make sure to upsert all of the data.
        '''
        
        self.query_agent = create_react_agent(
            model=self.llm,
            tools=create_connector_tool(self.connector_builder),
            prompt=self.query_prompt,
        ) 
        
        self.formatter_agent = create_react_agent(
            model=self.llm,
            tools=list_namespace_ids_tool(self.dbutils),
            prompt=self.formatter_prompt,
            response_format=PineconeSchemaHolder
        )
        
        self.upserter_agent = create_react_agent(
            model=self.llm,
            tools=[create_upserter_tool(self.dbutils)],
            prompt=self.upserter_prompt
        )
        self.graph = self.construct_graph()

    def construct_graph(self):
        builder = StateGraph(IntegrationState)
        builder.add_node("query_node", self.query_node)
        builder.add_node("formatter_node", self.formatter_node)
        builder.add_node("upserter_node", self.upserter_node)

        builder.add_edge(START, "query_node")
        builder.add_edge("query_node", "formatter_node")
        builder.add_edge("formatter_node", "upserter_node")
        builder.add_edge("upserter_node", END)
 
        return builder.compile()
 
    def query_node(self, state: IntegrationState) -> Command[Any]:
        result = self.query_agent.invoke(input=state, config={"callbacks": self.callbacks})
        print(result["messages"][-1].pretty_print())
        return Command(
            update={
                "messages": [
                    HumanMessage(content=result["messages"][-1].content, name='query')
                ]
            }
        )
 
    def similarity_node(self, state: IntegrationState):
        pass
    def formatter_node(self, state: IntegrationState) -> Command[Any]:
        result = self.formatter_agent.invoke(input=state, config={"callbacks": self.callbacks})
        result = result["structured_response"]
        actual_message = result.repr()
        print(actual_message)

        return Command(
            update={
                "messages": [
                    HumanMessage(content=str(actual_message), name="format")
                ]
            }
        ) 

    def upserter_node(self, state: IntegrationState) -> Command[Any]:
        result = self.upserter_agent.invoke(input=state, config={"callbacks": self.callbacks})
        print(result["messages"][-1].pretty_print())

        return Command(
            update={
                "messages": [
                    HumanMessage(content=result["messages"][-1].content, name="upsert")
                ]
            }
        )
