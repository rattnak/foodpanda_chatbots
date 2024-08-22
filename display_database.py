import time
import sqlite3

def display_database(interval=5):
    while True:
        try:
            # Connect to the SQLite database
            with sqlite3.connect("database.db") as conn:
                cursor = conn.cursor()
                
                # Execute a query to fetch all data from the orders table
                cursor.execute("SELECT * FROM orders")
                
                # Fetch all rows from the executed query
                rows = cursor.fetchall()
                
                # Print each row
                print("Current database contents:")
                for row in rows:
                    print(row)
        
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
        
        # Wait for the specified interval before querying again
        time.sleep(interval)

if __name__ == "__main__":
    display_database()
