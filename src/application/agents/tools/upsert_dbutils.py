from langchain_core.tools import tool
from typing import List

def create_upserter_tool(dbutils):
    
    @tool
    def upsert_dbutils(data: List[dict], namespace: str):
        """
        This tool upserts your data into pinecone. Just supply the data as its parameter.
        The namespace parameter is the name of the connector in the user query
        The return value is how many vectors we upserted.
        """
        embeddings = []
        vectors = []

        for i in range(0, len(data), 10):
            chunk = data[i:i + 10]
            embeddings += dbutils.create_embedding(chunk)
       
        for d, e in zip(data, embeddings):
            vectors.append({
                "id": d['id'],
                "values": e['values'],
                "metadata": {'text': d['text']}
            }) 
        result = dbutils.upsert_embeddings("quickstart", namespace, vectors)
        return result
    return upsert_dbutils
