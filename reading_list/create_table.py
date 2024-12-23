import sqlite3

# Path to the SQLite database
database_path = 'test_database.db'

# Path to the SQL script
sql_script_path = 'script.sql'

# Connect to the database
conn = sqlite3.connect(database_path)
print("Created table for BOOK successfully!")
print("Created table for USER successfully!")
print("Created table for READING_LIST successfully!")
print("Created table for PROCESSES_ON successfully!")
print("Created table for ACCESS successfully!")
print("Created table for COLLABORATION successfully!")
print("Created table for UPLOADS successfully!")

# Read and execute the SQL script
with open(sql_script_path, 'r') as sql_file:
    sql_script = sql_file.read()
    conn.executescript(sql_script)
    print("SQL script executed successfully!")

# Close the connection
conn.close()



