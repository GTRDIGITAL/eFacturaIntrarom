import pandas as pd
import requests

# Încarcă fișierul Excel într-un DataFrame
df = pd.read_excel("C:/Dezvoltare/E-Factura/2023/Baze de vanzari/CUI.xlsx")

# Inițializează lista pentru a stoca datele din API
# date_api_complete = []
info=[]
dataCautare = '2020-11-01'
# URL-ul API-ului
url_api = 'https://webservicesp.anaf.ro/PlatitorTvaRest/api/v8/ws/tva'

# Pentru fiecare rând din DataFrame
for index, row in df.iterrows():
    # Scoate "RO" din CUI dacă este prezent
    cui_without_prefix = str(row['CUI']).replace('RO', '')

    # Construiește obiectul JSON pentru cererea API
    payload = [{'cui': cui_without_prefix, 'data': str(dataCautare)}]

    # Efectuează solicitarea API
    response = requests.post(url_api, json=payload)

    # Verifică dacă solicitarea a avut succes (status code 200)
    # try:
    if response.status_code == 200:
        # Extrage datele din răspunsul API
        date_api_complete = response.json()
        # print(date_api_complete)
        cui=str(date_api_complete['found'][0]['date_generale']['cui'])
        regiune=str(date_api_complete['found'][0]["adresa_domiciliu_fiscal"]['dcod_JudetAuto'])
        denumire=str(date_api_complete['found'][0]['date_generale']['denumire'])
        adresa=str(date_api_complete['found'][0]['date_generale']['adresa'])
        # print(cui)
        # print(regiune)
        # print(denumire)
        # print(adresa)
        info_dict = {
        cui: {
            'regiune': regiune,
            'denumire': denumire,
            'adresa': adresa
        }
    }
        info.append(info_dict)
        
    else:
        
        print(f'Eroare la solicitarea pentru CUI-ul {cui_without_prefix}')
    # except:
    #     # Tratează cazul în care solicitarea a eșuat
    #         # print(date_api_complete)
    #         # print(cui)
    #         pass
            

print(info)
