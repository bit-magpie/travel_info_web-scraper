import time
from utils.logging import Logger
from app.db_api.db_operations import execute_query

logger = Logger()

def main():
    query = """
    CREATE TABLE IF NOT EXISTS locations (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100),
        country VARCHAR(100),
        coordinates VARCHAR(100)
    );
    """
    execute_query(query)


if __name__ == "__main__":

    logger.info("executing create table query")
    main()

