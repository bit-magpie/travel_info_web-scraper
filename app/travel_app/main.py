from travel_app.utils.logging import logger
from travel_app.db_api.db_operations import execute_query
from travel_app.db_api.create_database import create_database



def main():
    create_database()


if __name__ == "__main__":
    logger.info("Executing create, insert, and select queries")
    main()

