from application.seeds.seed_parser import BaseSeedParser
from application.dbutils import DbUtils
import csv


class CSVParser(BaseSeedParser):
    
    def __init__(self, file_path:str, index_name:str, namespace:str, dbutils:DbUtils):
        super().__init__(file_path, index_name, namespace, dbutils)
        self.data= []
        self.embeddings = []
        self.vectors = []
        self.dimensions = 0

    def load_data(self):
        with open(self.file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            self.data = [row for row in reader]
 
            # if the index we are pushing to exists, use its dimensionality
            if self.dbutils.index_exists(self.index_name):
                self.dimensions = self.dbutils.describe_index(self.index_name).index.dimension
            else:
                self.dimensions = 1024
                self.dbutils.create_index(self.index_name, self.dimensions)

    # create a new field on each row, that is a concat of all the fields values
    def parse_data(self):
        result = []
        for key, item in enumerate(self.data):
            squished_data = ', '.join(str(value) for value in item.values())
            result.append({
                'id': str(key), 
                'text': squished_data
            })
        self.data = result

    def to_vector(self):
        for i in range(0, len(self.data), self.dbutils.generator_batch_size):
            chunk = self.data[i:i + self.dbutils.generator_batch_size]
            self.embeddings += self.dbutils.create_embedding(chunk)
        
        for d, e in zip(self.data, self.embeddings):
            self.vectors.append({
            "id": d['id'],
            "values": e['values'],
            "metadata": {'text': d['text']}
        })

    # We are batch upserting the vector embeddings here.
    def save_vectors(self):
        self.dbutils.upsert_embeddings(self.index_name, self.namespace, self.vectors)