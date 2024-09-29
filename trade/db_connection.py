import oracledb

def get_db_connection():
    dsn = oracledb.makedsn("34.47.123.172", 8521, service_name="FREEPDB1")
    connection = oracledb.connect(user="developer", password="!A12341234", dsn=dsn)
    return connection
