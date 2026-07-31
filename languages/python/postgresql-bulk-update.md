# postgresql bulk update with python

## How to use `psycopg2.extras.execute_values`  to do bulk insert against postgreSQL table 

```python
import psycopg2
import psycopg2.extras

conn = psycopg2.connect(<your_database_connection_string>)
cur = conn.cursor()

# Example data to insert
data = [(1, "John"), (2, "Jane"), (3, "Jim")]

# SQL INSERT statement with placeholders
insert_sql = "INSERT INTO your_table (column1, column2) VALUES %s"

# Use the execute_values method to perform the bulk insert
psycopg2.extras.execute_values(cur, insert_sql, data)

# Commit the transaction
conn.commit()

# Close the cursor and connection
cur.close()
conn.close()

```

## How to do it when the primary key of the table is a sequence 


If the table has a sequence as the primary key, you can still use psycopg2.extras.execute_values to perform a bulk insert. You just need to modify the INSERT statement to use the nextval function from the pg_sequences to get the next value from the sequence for each row being inserted.


```python
import psycopg2
import psycopg2.extras

conn = psycopg2.connect(<your_database_connection_string>)
cur = conn.cursor()

# Example data to insert
data = [(1, "John"), (2, "Jane"), (3, "Jim")]

# SQL INSERT statement with placeholders
insert_sql = "INSERT INTO your_table (id, column1, column2) VALUES (%s, %s, %s)"

# Use the execute_values method to perform the bulk insert
psycopg2.extras.execute_values(cur, insert_sql, data, template="(nextval('your_sequence'), %s, %s)", page_size=1000)

# Commit the transaction
conn.commit()

# Close the cursor and connection
cur.close()
conn.close()

```

In this example, the execute_values method will automatically create a batch of multiple INSERT statements, each with a call to the nextval function to get the next value from the sequence for the id column. The batch size can be specified by passing the page_size argument to the method.

## How to do it when the table contains a json type column

use `json.dumps` to dumps object to string, before insert into json field.

```python
import psycopg2
import psycopg2.extras
import json

conn = psycopg2.connect(<your_database_connection_string>)
cur = conn.cursor()

# Example data to insert
data = [(1, "John", json.dumps({'age': 30, 'address': '123 Main St.'})),
        (2, "Jane", json.dumps({'age': 35, 'address': '456 Elm St.'})),
        (3, "Jim", json.dumps({'age': 40, 'address': '789 Oak St.'}))]

# SQL INSERT statement with placeholders
insert_sql = "INSERT INTO your_table (column1, column2, json_column) VALUES %s"

# Use the execute_values method to perform the bulk insert
psycopg2.extras.execute_values(cur, insert_sql, data)

# Commit the transaction
conn.commit()

# Close the cursor and connection
cur.close()
conn.close()

```

## Deal with json type column using `psycopg2.extras.Json`

`psycopg2.extras.Json` is a type adapter provided by the `psycopg2` library for handling JSON data in Python. It allows you to insert JSON data into a PostgreSQL database using the psycopg2 library and have it automatically converted to the appropriate format for storage in the database.

Here's an example of how you can use psycopg2.extras.Json:

```python
import psycopg2
import psycopg2.extras

conn = psycopg2.connect(<your_database_connection_string>)
cur = conn.cursor()

# Example JSON data
json_data = {'age': 30, 'address': '123 Main St.'}

# SQL INSERT statement with placeholders
insert_sql = "INSERT INTO your_table (json_column) VALUES (%s)"

# Use the execute method to insert the JSON data
cur.execute(insert_sql, (psycopg2.extras.Json(json_data),))

# Commit the transaction
conn.commit()

# Close the cursor and connection
cur.close()
conn.close()

```

## Update a field of Json type column

table: users
columns: 
        name: string
        property: {"height":1.74, "weight": 67, "skills": {"python":"good", "typescript": "excellent"}}

```python
import psycopg2
import psycopg2.extras

conn = psycopg2.connect(<your_database_connection_string>)
cur = conn.cursor()

skills = {
        "csharp": "proficient",
        "jenkins": "master"
}
updateSql = """update users
        set property = jsonb_set(property, '{skills}', '%s', true)
        where name = '%s'
""" % (json.dumps(skills), "phil")

cur.execute(updateSql)

# Commit the transaction
conn.commit()

# Close the cursor and connection
cur.close()
conn.close()

```