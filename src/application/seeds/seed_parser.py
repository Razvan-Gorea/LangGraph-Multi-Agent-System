from application.dbutils import DbUtils

# ABSTRACT
class BaseSeedParser(object):
    def __init__(self, file_path:str, index_name:str, namespace:str, dbutils:DbUtils):
        self.file_path = file_path
        self.index_name = index_name
        self.dbutils = dbutils
        self.namespace = namespace

    def load_data(self):
        return

    def parse_data(self):
        return

    def to_vector(self):
        return

    def save_vectors(self):
        return
