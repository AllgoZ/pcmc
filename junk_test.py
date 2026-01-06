import psycopg2

def display_auth_user_column(database_name, user, password, host, port, column_name):
    connection = None
    cursor = None

    try:
        connection = psycopg2.connect(
            database=database_name,
            user=user,
            password=password,
            host=host,
            port=port
        )
 
        cursor = connection.cursor()

   
        cursor.execute("""
            SELECT 1 
            FROM information_schema.tables 
            WHERE table_name = 'auth_user' AND table_schema = 'public'
        """)

        table_result = cursor.fetchone()
        
        if table_result:
            print(f"Table 'auth_user' exists in database '{database_name}'. Displaying '{column_name}' column:")
            
            # Fetch the specified column from auth_user table
            cursor.execute(f"SELECT {column_name} FROM auth_user")
            rows = cursor.fetchall()
            
            # Display the content of the specified column
            for row in rows:
                print(row[0])  # Assuming you are fetching a single column, use index 0

        else:
            print(f"Table 'auth_user' does not exist in database '{database_name}'.")
        
    except Exception as e:
        print(f"Error: {e}")
        
    finally:
        # Close the cursor and connection
        if cursor:
            cursor.close()
        if connection:
            connection.close()

# Replace these with your PostgreSQL server details
database_name = "pcmc_db"
user = "pcmc_admin"
password = "tepros@123"
host = "127.0.0.1"
port = "5432"
column_name = "username"  # Replace with the desired column name

# Call the function
display_auth_user_column(database_name, user, password, host, port, column_name)
