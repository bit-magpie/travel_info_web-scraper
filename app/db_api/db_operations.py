import psycopg2
from utils import logger

# Database connection details
DB_HOST = "db"  # The 'db' is the name of the service in Docker Compose
DB_PORT = "5432"
DB_NAME = "travel_db"
DB_USER = "postgres"
DB_PASSWORD = "postgres"

# Establishing the connection
def get_db_connection():
    """Create and return a database connection."""
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    return conn

def execute_query(query: str) -> str:
    """Execute a query and prints output as text."""
    try:
        # Establish the database connection
        logger.info(f"Executing query: {query}")
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Execute the provided query
        cursor.execute(query)

        output = ""

        # If it's a SELECT query, fetch the results
        if query.strip().lower().startswith("select"):
            results = cursor.fetchall()
            # Format results as a string for display
            output = "\n".join([str(row) for row in results])
            logger.info(f"Query result: {output}")  # Log query result
        else:
            # Commit changes for CREATE, INSERT, UPDATE queries
            conn.commit()
            logger.info("Query executed successfully and changes committed.")

        cursor.close()
        conn.close()        
        
        logger.info(output)

    except Exception as e:
        logger.error(f"Error executing query: {str(e)}")
        return str(e)