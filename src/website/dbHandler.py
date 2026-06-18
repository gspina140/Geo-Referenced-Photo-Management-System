import psycopg2

class DbHandler:
    def __init__(self) -> None:
        try:
            self.connection = psycopg2.connect(host="localhost", database="casproject_db", user="postgres", password="postgres")
        except psycopg2.Error as e:
            print(f"Unable to connect to DB: {e}")
            exit()
            
        self.cursor = self.connection.cursor()
    
    def exec_query(self,query, args=""):
        try:
            self.cursor.execute(query, args)
        except psycopg2.Error as e:
            print(f"Unable to execute query: {e}")
            return None
            
        return self.cursor.fetchall()
    
    def exec_insert_query(self, query, args=""):
        try:
            self.cursor.execute(query, args)
            self.connection.commit()
        except psycopg2.Error as e:
            print(f"Unable to execute query: {e}")
            return None
            
        return self.cursor.fetchall()    