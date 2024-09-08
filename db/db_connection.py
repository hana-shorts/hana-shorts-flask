import oracledb

def get_db_connection():
    connection = oracledb.connect(
        user="developer",
        password="!A12341234",
        dsn="34.47.85.59:8521/FREEPDB1"
    )

    return connection
