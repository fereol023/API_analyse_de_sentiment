import uuid, os
from cassandra.cluster import Cluster
from dotenv import load_dotenv
load_dotenv()


class CassandraDB:
    def __init__(self):
        # CASSANDRA_HOST = os.getenv('CASSANDRA_HOST', None)
        CASSANDRA_HOST = '15.188.123.88'
        cluster = Cluster([CASSANDRA_HOST]) # liste des serveurs
        try:
            self.session = cluster.connect()
            # print(self.session)
            # creation bdd
            self.session.execute(
                """
                CREATE KEYSPACE IF NOT EXISTS my_keyspace
                WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1}
                """
                )
            self.session.set_keyspace('my_keyspace') # KEYSPACE est equivalent à database en sql

            self.session.execute(
                """
                CREATE TABLE IF NOT EXISTS session_avis (
                    client_id UUID PRIMARY KEY,
                    text TEXT,
                    note INT
                )
                """
            )
            print(f"Connexion ok avec le serveur db !")
        except:
            print(f"Erreur lors du chargement de la session")
        ## dbeaver

    def insert_user(self, session, text, note):
        client_id = uuid.uuid4()
        try:
            session.execute("""
                INSERT INTO session_avis (client_id, text, note) VALUES (%s, %s, %s)
            """, (client_id, text, note))
        except Exception as e:
            print(f"Error insertion in session_avis : {e}: client_id: {client_id}, text : {text}")

    # Recuperation et affichage des utilisateurs
    def fetch_avis(self):
        res = []
        rows = self.session.execute("SELECT text FROM session_avis")
        for row in rows:
            # print(f"Avis: {row.text}")
            res.append(row.text)
        return res

    def fetch_notes(self):
        res = []
        rows = self.session.execute("SELECT note FROM session_avis")
        for row in rows:
            # print(f"Note: {row.note}")
            res.append(row.note)
        return res


    def load_avis_db(self):
        with open('data/dataset.txt', 'r') as f:
            content = f.readlines()
            content = list(map(lambda t: t.replace('\n', ''), content))
            content = list(map(lambda t: tuple(t.split("   ")), content))
            content = list(map(lambda t: {'text': t[0], 'note': int(t[1])}, content))
        return content

    def insert_all_avis(self, data):
        for d in data: # ou threading
            self.insert_user(session=self.session, **d)
        print(f"{len(data)} rows inserted !")


if __name__=='__main__':
    # ----- exec
    DB = CassandraDB()
    # # DB.insert_all_avis(DB.load_avis_db())
    DB.fetch_avis()