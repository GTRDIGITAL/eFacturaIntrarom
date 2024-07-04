# import pandas as pd
# from sqlalchemy import create_engine
# import json

# def citeste_configurare(file_path):
#     with open(file_path, 'r') as file:
#         config = json.load(file)
#     return config

# config = citeste_configurare('config.json')
# mysql_config = config['mysql']

# # db_url = 'mysql://userAdmin:some_pass@192.168.1.222/efacturaferro'
# db_url = f"mysql://{config['mysql']['user']}:{config['mysql']['password']}@{config['mysql']['host']}/{config['mysql']['database']}"

# engine = create_engine(db_url)

# nume_tabel = 'clients'
# df_excel = pd.read_excel("C:/Dezvoltare/E-Factura/2023/Baze de vanzari/outs/client.xlsx", sheet_name='Sheet1')

# # Specifică if_exists='append' pentru a adăuga date la tabela existentă
# df_excel.to_sql(nume_tabel, engine, if_exists='append', index=False)

# # # Afisează datele din tabela Clients după adăugare
# # result = pd.read_sql_query(f'SELECT * FROM {nume_tabel}', engine)
# # print(result)
import pandas as pd
import pymysql
import json
def citeste_configurare(file_path):
    with open(file_path, 'r') as file:
        config = json.load(file)
    return config

config = citeste_configurare('config.json')
mysql_config = config['mysql']

# Conectare la baza de date MySQL
connection = pymysql.connect(host=mysql_config['host'],
    user=mysql_config['user'],
    password=mysql_config['password'],
    database=mysql_config['database'])

# Deschideți fișierul Excel
df = pd.read_excel("C:/Dezvoltare/E-Factura/2023/eFactura/Konica/eFacturaKonicaMinolta/Baza de date vanzari/CUI CLIENTI KONICA.xlsx")

# Extrageți valorile din coloanele dorite
valori_regno = df['CUI']


# Definiți comanda SQL de inserare
sql = "INSERT INTO clients (regno) VALUES (%s)"

# Executați comanda SQL pentru fiecare pereche de valori din coloanele corespunzătoare
with connection.cursor() as cursor:
    for regno in zip(valori_regno):
        cursor.execute(sql, (regno))
    
# Faceți commit pentru a salva modificările în baza de date
connection.commit()

# Închideți conexiunea la baza de date
# connection.close()
