from mongoengine import connect

from minesweeper.config import config


def connect_to_mongo_db():
    """
    """
    db_config = config['database']
    connect(
        db=db_config['name'],
        host=db_config['host'],
        port=db_config['port'],
        username=db_config['username'],
        password=db_config['password'],
        authentication_source='admin'
    )
