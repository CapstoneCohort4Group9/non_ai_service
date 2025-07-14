import psycopg2


db_host = "hopjetair-postgres.cepc0wqo22hd.us-east-1.rds.amazonaws.com"


db_name = "hopjetair"
db_user = "hopjetair"
db_pass = "SecurePass123!"


#db_name = "postgres"


db_host = "localhost"

# db_name = "hopjetairline_db"
# db_user = "postgres"
# db_pass = "Testing!@123"




# db_host = "localhost"

# db_name = "postgres"
# db_user = "postgres"
# db_pass = "Testing!@123"


connection = psycopg2.connect(host = db_host, database =  db_name, user = db_user, password = db_pass)

#connection = psycopg2.connect("postgresql://hopjetair:SecurePass123!@localhost:5432/hopjetairline_db")
print("connected to the databaser")
print(connection.get_dsn_parameters()['host'])  # Output: localhost
cursor = connection.cursor()
cursor.execute("Select 1")
db_version = cursor.fetchone()
print(db_version)



cursor.close()