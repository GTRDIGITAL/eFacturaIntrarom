import mysql.connector
import json

def citeste_configurare(file_path):
    with open(file_path, 'r') as file:
        config = json.load(file)
    return config

config = citeste_configurare('config.json')
mysql_config = config['mysql']

# Conectează-te la noua bază de date
mydb = mysql.connector.connect(
    host=mysql_config['host'],
    user=mysql_config['user'],
    password=mysql_config['password'],
    database=mysql_config['database']
)
# Creează un cursor pentru a executa comenzi SQL
# mycursor = mydb.cursor()

# # Definește instrucțiunea SQL pentru a modifica structura tabelei
# # sql = "ALTER TABLE FisierePDF MODIFY COLUMN data_introducere DATETIME"
# sql="select * from fisierepdf"
# print(sql)

# # Execută instrucțiunea SQL
# mycursor.execute(sql)

# # Confirmă modificările în baza de date
# # mydb.commit()

# # Închide cursorul și conexiunea la baza de date
# mycursor.close()
# mydb.close()


# Creează un cursor pentru a executa comenzi SQL
mycursor = mydb.cursor()

# Definește instrucțiunea SQL pentru a modifica structura tabelei
# sql = "SELECT nume_fisier, data_introducere FROM FisierePDF"
sql='select * from statusmesaje where tip ="FACTURI PRIMITE"'
# Execută instrucțiunea SQL
mycursor.execute(sql)

# Ia toate rândurile din rezultatul interogării
rezultate = mycursor.fetchall()

# Afisează fiecare rând din rezultate
for rand in rezultate:
    print(rand)

# Închide cursorul și conexiunea la baza de date
mycursor.close()
mydb.close()