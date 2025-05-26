from pinecone import Pinecone, ServerlessSpec, Index, QueryResponse, IndexModel, NotFoundException
from application.environment import Environment
from itertools import *
from typing import Any, Dict, List

class DbUtils(object):

    def __init__(self, env:Environment, generator_batch_size:int, upsert_batch_size:int, embedding_model:str):
        self.env = env
        self.client = self.get_client(env)
        self.generator_batch_size = generator_batch_size
        self.upsert_batch_size = upsert_batch_size
        self.embedding_model = embedding_model
    
    def get_client(self, env:Environment) -> Pinecone:
        pc_client = Pinecone(api_key=env.PINECONE_API_KEY)
        return pc_client

    def get_index(self, index_name:str) -> Index:
        return self.client.Index(index_name)

    def create_index(self, index_name:str, dimension:int) -> None:
        # hardcoded value are to stay within the free tier
        self.client.create_index(
            name=index_name,
            dimension=dimension,
            metric="cosine",
            spec=ServerlessSpec(
            cloud="aws",
            region="us-east-1"
            )
        )
    
    # we expect an attribute in each row called text
    # inputs must match the length the embedding model supports
    def create_embedding(self, data:list[Dict]) -> list[dict]:
        embeddings = self.client.inference.embed(
            model=self.embedding_model,
            inputs=[d['text'] for d in data],
            parameters={"input_type": "passage", "truncate": "END"}
        )
        if self.env.DEBUG_MODE:
            print("Embedding created")
        
        return embeddings

    def create_query_embedding(self, query:str) -> list[dict]:
        embedding = self.client.inference.embed(
            model=self.embedding_model,
            inputs=[query],
            parameters={
                "input_type": "query"
            }
        )
        if self.env.DEBUG_MODE:
            print("Embedding created")
        
        return embedding.data[0].values
    
    def upsert_chunker(self, iterable:list[dict], batch_size:int):
        it = iter(iterable)
        chunk = tuple(islice(it, batch_size))
        while chunk:
            yield chunk
            chunk = tuple(islice(it, batch_size))
    
    def upsert_embeddings(self, index_name:str, namespace:str, embeddings:list[dict]) -> int:

        total_upserted = 0
        index = self.get_index(index_name);

        for ids_vectors_chunk in self.upsert_chunker(embeddings, self.upsert_batch_size):
            response = index.upsert(
                vectors=ids_vectors_chunk,
                namespace=namespace
            )

            if self.env.DEBUG_MODE:
                print("Embedding upserted")

            total_upserted += response["upserted_count"]

        return total_upserted

    def search(self, index_name:str, namespace:str, embedding: list[float], result_amount:int) -> list[Dict]:
        # pass in .data of the embedding here
        index = self.get_index(index_name)
        results = index.query(
            namespace=namespace,
            vector=embedding,
            top_k=result_amount,
            include_values=False,
            include_metadata=True
        )
        return results.matches
    
    def index_exists(self, index_name:str) -> bool:
        try:
            self.client.describe_index(index_name)
            return True
        except NotFoundException:
            return False
    
    def describe_index(self, index_name:str) -> IndexModel:
        return self.client.describe_index(index_name)
    
    def get_namespaces(self, index_name:str) -> List:
        index = self.get_index(index_name)
        response = index.describe_index_stats()
        namespaces = response.get('namespaces', {})

        namespaces_as_list = list(namespaces.keys())

        if len(namespaces_as_list) > 0:
            return namespaces_as_list
        return []
    
    def list_ids_in_namespace(self, index_name: str, prefix: str, namespace:str):
        index = self.get_index(index_name)
        return index.list(prefix=prefix, limit=10, namespace=namespace)

