from flask import request, render_template
import openpyxl
import datetime
import requests
import os
import pymysql
import json
def citeste_configurare(file_path):
    with open(file_path, 'r') as file:
        config = json.load(file)
    return config

config = citeste_configurare('config.json')
mysql_config = config['mysql']

def CUI_process():
    # Conectare la baza de date MySQL
    connection = pymysql.connect(host=mysql_config['host'],
    user=mysql_config['user'],
    password=mysql_config['password'],
    database=mysql_config['database'])

    # Creați un cursor pentru a executa interogările SQL
    cursor = connection.cursor()

    try:
        # Interogați baza de date pentru a obține toate valorile din coloana `regno`
        cursor.execute("SELECT regno FROM clients where name=''")
        # Obțineți toate valorile din interogare
        regno_cust_values = cursor.fetchall()

        # Parcurgem fiecare înregistrare din interogare
        for regno_tuple in regno_cust_values:
            regno = regno_tuple[0]  # Extract the string value from the tuple
            ccc = []
            dataCautare = datetime.datetime.now().date()
            print(dataCautare)
            try:
                if "RO" in regno or "RO " in regno:
                    b = regno.replace("RO", "").replace(" ","")  # Use regno directly
                    ccc.append(b)
                else:
                    ccc.append(regno)

                listaUnicaCui = list(set(ccc))

                for cui in listaUnicaCui:
                    cui_without_prefix = cui.replace('RO', '')  # Elimină prefixul "RO" din CUI
                    payload = [{'cui': cui_without_prefix, 'data': str(dataCautare)}]
                    response = requests.post('https://webservicesp.anaf.ro/PlatitorTvaRest/api/v8/ws/tva', json=payload)
                    
                    if response.status_code == 200:
                        date_api_complete = response.json()
                        
                        if 'found' in date_api_complete and date_api_complete['found']:
                            for found_item in date_api_complete['found']:
                                clientName = str(found_item["date_generale"]["denumire"])
                                country = 'RO'
                                cui = str(found_item['date_generale']['cui'])
                                city = str(found_item["adresa_domiciliu_fiscal"]["ddenumire_Localitate"])
                                street = str(found_item["adresa_domiciliu_fiscal"]["ddenumire_Strada"]) + " " + str(found_item["adresa_domiciliu_fiscal"]["dnumar_Strada"])
                                regiune = str(found_item["adresa_domiciliu_fiscal"]['dcod_JudetAuto'])
                                
                                # Corectare a variabilei "sector"
                                sector = "SECTOR" + str(found_item["adresa_domiciliu_fiscal"]["dcod_Localitate"])

                                # Actualizăm baza de date cu informațiile obținute din API
                                try:  
                                    if 'Sector' in city:
                                        cursor.execute("UPDATE clients SET name = %s, country = %s, city = %s, street = %s, region = %s WHERE regno = %s", 
                                                    (clientName, country, sector, street, regiune, regno))
                                        print(clientName, country, sector, street, regiune, regno)
                                    else:
                                        cursor.execute("UPDATE clients SET name = %s, country = %s, city = %s, street = %s, region = %s WHERE regno = %s", 
                                                    (clientName, country, city, street, regiune, regno))
                                        print("aici nu e sector")
                                except Exception as e:
                                    print(f'Eroare la actualizarea bazei de date: {e}')
                        else:
                            print(f'Nu s-au găsit informații pentru CUI-ul: {cui_without_prefix}')
                    else:
                        print(f'Eroare la solicitarea către API: Cod de stare {response.status_code}')
            except:
                print("nu e RO")
    except Exception as e:
        print(f'Eroare: {e}')
    finally:
        # Facem commit după ce am terminat operațiile cu baza de date
        connection.commit()
        # Închideți conexiunea la baza de date
        # connection.close()

# Apelăm funcția principală pentru procesare
CUI_process()
