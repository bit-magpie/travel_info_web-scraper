import psycopg2

# Database connection details
DB_HOST = "db"  # The 'db' is the name of the service in Docker Compose
DB_PORT = "5432"
DB_NAME = "travel_db"
DB_USER = "myuser"
DB_PASSWORD = "mypassword"

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
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Execute the provided query
        cursor.execute(query)

        output = ""

        # If it's a SELECT query, fetch the results
        if query.strip().lower().startswith("select"):
            results = cursor.fetchall()
            # Format results as a string for display
            for row in results:
                output += str(row) + "\n"
        else:
            # Commit changes for CREATE, INSERT, UPDATE queries
            conn.commit()


        cursor.close()
        conn.close()        
        
        print(output)

    except Exception as e:
        return f"Error: {e}"