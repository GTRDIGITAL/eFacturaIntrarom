import datetime
import json
import time
import pymysql
import requests
from stocareBD import stocareMesajeAnaf2, stocarePDFPrimite
import os
import shutil
import zipfile

def citeste_configurare(file_path):
    with open(file_path, 'r') as file:
        config = json.load(file)
    return config

config = citeste_configurare('config.json')
mysql_config = config['mysql']
dateFirma = config['dateFirma']
headers = {'Authorization': dateFirma['header']}
cif = dateFirma['cui']

def stergeFisiere(directory_path, file_extension):
        try:
            for filename in os.listdir(directory_path):
                file_path = os.path.join(directory_path, filename)
                if filename.endswith(file_extension):
                    os.remove(file_path)
                    print(f"Fisierul {filename} a fost sters.")
        except Exception as e:
            print(f"Eroare la stergerea fișierelor: {str(e)}")

    
    
def interogareIDprimite():
    connection = pymysql.connect(
        host=mysql_config['host'],
        user=mysql_config['user'],
        password=mysql_config['password'],
        database=mysql_config['database']
    )
    cursor = connection.cursor()
    
    selectQuery = "SELECT distinct id_factura FROM statusmesaje2 WHERE tip ='FACTURA PRIMITA'"
    cursor.execute(selectQuery)
    result_list = [row[0] for row in cursor.fetchall()]
    cursor.close()
    connection.close()
    return result_list


def sincronizareAPIvsBD():
    result_list = interogareIDprimite()
    # print("result list ", len(result_list), result_list)
    # set_result_list = set(result_list)  # Convertim lista în set pentru căutare eficientă

    time.sleep(10)
    
    current_time = datetime.datetime.now()
    start_time = current_time - datetime.timedelta(days=60)
    val1 = int(time.mktime(start_time.timetuple())) * 1000

    X = 0
    result = datetime.datetime.now() - datetime.timedelta(seconds=X)
    val2 = int(datetime.datetime.timestamp(result) * 1000)

    print("val1 ", val1)
    print("val2 ", val2)

    apiListaFacturi = f'https://api.anaf.ro/prod/FCTEL/rest/listaMesajePaginatieFactura'

    params = {
        'startTime': val1,
        'endTime': val2,
        'cif': cif,
        'pagina': 1
    }

    while True:
        try:
            response = requests.get(apiListaFacturi, params=params, headers=headers)

            if response.status_code == 200:
                data = response.json()
                if 'eroare' in data:
                    time.sleep(5)
                else:
                    numar_pagini = data.get('numar_total_pagini')
                    print(numar_pagini, 'numar pagini')
                    api_url_updated = f'{apiListaFacturi}?startTime={val1}&endTime={val2}&cif={cif}&pagina={numar_pagini}'

                    listaMesaje = requests.get(api_url_updated, headers=headers, timeout=30)
                    if listaMesaje.status_code == 200:
                        raspunsMesajeFacturi = listaMesaje.json()
                        listaIDANAF = [int(mesaj['id']) for mesaj in raspunsMesajeFacturi['mesaje'] if mesaj['tip'] == 'FACTURA PRIMITA']

                        # print("Lista ID-uri ANAF: ", listaIDANAF, "lungimea id anaf ", len(listaIDANAF))

                        # Convertirea ID-urilor în întregi
                        result_list = [int(id) for id in result_list]

                        listaDiferente = [id for id in listaIDANAF if id not in result_list]

                        # print("Lista diferențe: ", listaDiferente, "lungimea diferente ", len(listaDiferente))
                        print("Lista diferențe: ", listaDiferente)
                        # Filtrarea mesajelor pentru a păstra doar cele din listaDiferente
                        
                        listaDiferente = [str(id) for id in listaDiferente]
                        mesajeFiltrate = [mesaj for mesaj in raspunsMesajeFacturi['mesaje'] if mesaj['id'] in listaDiferente]
                        rezultat_final = {'mesaje': mesajeFiltrate}
                        # print(mesajeFiltrate)
                        # Stocare mesaje filtrate
                        print("urmeaza insert")
                        stocareMesajeAnaf2(rezultat_final)
                        # print(rezultat_final)
                        print('Stocare a mesajelor cu success')
                        break
                    else:
                        print(f'Eroare la cererea API, cod de stare: {listaMesaje.status_code}')
                        time.sleep(10)
            else:
                time.sleep(10)
        except KeyError as e:
            print(e)
            time.sleep(10)
        except Exception as e:
            print(f'Eroare: {e}')
            time.sleep(10)
            
    def descarcare():
        for i in range(0, len(listaDiferente)):
            apiDescarcare = 'https://api.anaf.ro/prod/FCTEL/rest/descarcare?id='+str(listaDiferente[i])

            descarcare = requests.get(apiDescarcare, headers=headers, timeout=30)

            if descarcare.status_code == 200:
                # print("Cererea a fost efectuata cu succes!")
                with open('C:/Dezvoltare/E-Factura/2023/eFactura/Konica/eFacturaKonicaMinolta local/output zip api/fisier'+str(listaDiferente[i])+'.zip', 'wb') as file:
                # with open("/home/efactura/efactura_konica/outputZipAPI/fisier"+str(listaIdDescarcare[i])+'.zip', 'wb') as file:
                    file.write(descarcare.content)
                    print('Descarcat cu success')
                
            # print(descarcare.text)
            else:
                print("Eroare la efectuarea cererii HTTP:", descarcare.status_code)
                print(descarcare.text)
    print("aici descarcam folosind id_descarcare")
    descarcare()

    directory_path = 'C:/Dezvoltare/E-Factura/2023/eFactura/Konica/eFacturaKonicaMinolta local/output zip api'
    # directory_path = "/home/efactura/efactura_konica/outputZipAPI"

    output_directory = 'C:/Dezvoltare/E-Factura/2023/eFactura/Konica/eFacturaKonicaMinolta local/output conversie'
    # output_directory = "/home/efactura/efactura_konica/outputConversie"
    # arhiveANAF = "/home/efactura/efactura_konica/arhiveANAF"

    os.makedirs(output_directory, exist_ok=True)

    for filename in os.listdir(directory_path):
        # break
        if filename.endswith('.zip'):
            zip_file_path = os.path.join(directory_path, filename)
            with zipfile.ZipFile(zip_file_path, 'r') as zip_file:
                xml_files = [name for name in zip_file.namelist() if name.endswith('.xml') and "semnatura" not in name.lower()]
                for xml_file in xml_files:
                    with zip_file.open(xml_file) as file:
                        xml_data = file.read()
                        output_path = os.path.join(output_directory, xml_file)
                        with open(output_path, 'wb') as output_file:
                            output_file.write(xml_data)
                            
                            
    def make_archive(source, destination):
        base = os.path.basename(destination)
        name = base.split('.')[0]
        format = base.split('.')[1]
        archive_from = os.path.dirname(source)
        archive_to = os.path.basename(source.strip(os.sep))
        shutil.make_archive(name, format, archive_from, archive_to)
        shutil.move('%s.%s'%(name,format), destination)   
        
    stocarePDFPrimite()
    print('s-au stocat facturile primite')
    stergeFisiere('C:/Dezvoltare/E-Factura/2023/eFactura/Konica/eFacturaKonicaMinolta local/output conversie', '.zip')
      

print('Aici vedem mesajele ANAF')
sincronizareAPIvsBD()
