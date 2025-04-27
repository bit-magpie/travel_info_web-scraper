import time
from utils.logging import logger
from db_api.db_operations import execute_query
from scrapper.create_database import create_database



def main():
    create_database()


if __name__ == "__main__":
    logger.info("Executing create, insert, and select queries")
    main()

