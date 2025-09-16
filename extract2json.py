import sqlite3
import json

def export_to_json(db_name, table_name, output_json):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Query to select all data from the specified table
    query = f"SELECT * FROM {table_name}"
    cursor.execute(query)

    # Fetch all rows from the table
    rows = cursor.fetchall()

    # Get column names from the table
    column_names = [description[0] for description in cursor.description]

    # Convert the data to a list of dictionaries
    data = [dict(zip(column_names, row)) for row in rows]

    # Write the data to a JSON file
    with open(output_json, 'w') as json_file:
        json.dump(data, json_file, indent=4)

    # Close the database connection
    conn.close()

    print(f"Data from table '{table_name}' has been exported to '{output_json}'")

# Example usage
db_name = 'database.db'     # Replace with your database name
table_name = 'orders'   # Replace with your table name
output_json = 'FloorExpress.json'      # Replace with your desired output JSON file name

export_to_json(db_name, table_name, output_json)
