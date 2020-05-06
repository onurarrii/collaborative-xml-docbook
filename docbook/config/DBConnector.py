import psycopg2 as psycopg2
''' Use this module to prevent creating new connections everytime a DBDPersistency method is called. '''


hostname = 'localhost'
user = 'postgres'
password = 'root'
port = '5432'
database = 'hw'


def get_connection():
    #TODO maybe create a new connection and return it ?
    connection = psycopg2.connect(host=hostname, database=database, user=user, password=password, port=port)
    return connection
