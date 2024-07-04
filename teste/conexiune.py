from sqlalchemy import create_engine


import json

def citeste_configurare(file_path):
    with open(file_path, 'r') as file:
        config = json.load(file)
    return config

config = citeste_configurare('config.json')
mysql_config = config['mysql']
# print(mysql_config)


# Parametrii de conexiune
db_user = mysql_config['user']
db_password = mysql_config['password']
db_host = mysql_config['host']
db_name = mysql_config['database']

# Creare motor SQLAlchemy pentru conexiunea MySQL fără SSL/TLS
engine = create_engine(f"mysql+mysqldb://{db_user}:{db_password}@{db_host}/{db_name}")

print(engine)