from ..utils import logger
from ..db_api.db_operations import execute_query


def create_continents_table():
    """
    Create the continents table in the database.
    """
        # Query 1: Create the continents table
    create_continent_query = """
    CREATE TABLE IF NOT EXISTS continents (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL UNIQUE
    );
    """
    execute_query(create_continent_query)

    # Query 2: Insert data into the continents table
    insert_continent_data_query = """
    INSERT INTO continents (name) VALUES
    ('Africa'),
    ('Antarctica'),
    ('Asia'),
    ('Europe'),
    ('North America'),
    ('Australia'),
    ('South America')
    ON CONFLICT (name) DO NOTHING;  -- Ensures no duplicates if already inserted
    """
    execute_query(insert_continent_data_query)

    # Query 3: Select and fetch the inserted data from the continents table
    select_continent_query = """
    SELECT * FROM continents;
    """
    execute_query(select_continent_query)
    logger.info("Continents table created and populated successfully.")

def create_countries_table():
    try:
        query = """CREATE TABLE Country (
        ID INT PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        size FLOAT, -- assuming in square kilometers
        main_language VARCHAR(100),
        capital VARCHAR(100),
        population BIGINT,
        continent_id INT,
        FOREIGN KEY (continent_id) REFERENCES Continents(ID)
        );"""
        execute_query(query)
        logger.info("Countries table created successfully.")

        # Insert sample data into the countries table
        insert_query = """
        INSERT INTO Country (ID, name, size, main_language, capital, population, continent_id) VALUES
        (1, 'United States', 9833517, 'English', 'Washington D.C.', 331002651, 5),
        (2, 'Canada', 9984670, 'English/French', 'Ottawa', 37742154, 5),
        (3, 'Mexico', 1964375, 'Spanish', 'Mexico City', 128932753, 5),
        (4, 'Japan', 377975, 'Japanese', 'Tokyo', 126476461, 3),
        (5, 'Germany', 357022, 'German', 'Berlin', 83783942, 4),
        (6, 'France', 551695, 'French', 'Paris', 65273511, 4),
        (7, 'Brazil', 8515767, 'Portuguese', 'Brasilia', 212559417, 7),
        (8, 'Argentina', 2780400, 'Spanish', 'Buenos Aires', 45195777, 7),
        (9, 'Australia', 7692024, 'English', 'Canberra', 25499884, 6),
        (10, 'South Africa', 1219090, 'Afrikaans/English/Zulu/Xhosa', 'Cape Town', 59308690, 1)
        ON CONFLICT (ID) DO NOTHING; -- Ensures no duplicates if already inserted
        """
        execute_query(insert_query)
        logger.info("Sample data inserted into countries table successfully.")
    except Exception as e:
        logger.error(f"Error creating countries table: {e}")
        raise ValueError("Failed to create countries table") from e
    

def create_city_table():
    pass

def create_airport_table():
    pass

def create_place_table():
    pass

def create_database():
    try:
        create_continents_table()
    except Exception as e:
        logger.error(f"Error creating continents table: {e}")
        raise ValueError("Failed to create continents table") from e
    try:
        create_countries_table()
    except Exception as e:
        logger.error(f"Error creating countries table: {e}")
        raise ValueError("Failed to create countries table") from e
    try:
        create_city_table()
    except Exception as e:
        logger.error(f"Error creating city table: {e}")
        raise ValueError("Failed to create city table") from e
    try:
        create_airport_table()
    except Exception as e:
        logger.error(f"Error creating airport table: {e}")
        raise ValueError("Failed to create airport table") from e
    try:
        create_place_table()
    except Exception as e:
        logger.error(f"Error creating place table: {e}")
        raise ValueError("Failed to create place table") from e

