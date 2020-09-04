from peewee import Proxy
from peewee import SqliteDatabase

DATABASE_PROXY = Proxy()  # Create a proxy for our db.

def OpenSqliteDatabase(database_file):
    """
    """
    database = SqliteDatabase(database_file)
    # Configure our proxy to use the db we specified in config.
    DATABASE_PROXY.initialize(database)
    database.connect()
    return database
