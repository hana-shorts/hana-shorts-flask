import cx_Oracle

def get_db_connection():
    dsn = cx_Oracle.makedsn("34.47.123.172", 8521, service_name="FREEPDB1")
    connection = cx_Oracle.connect(user="developer", password="!A12341234", dsn=dsn)
    return connection
