import datetime
import os
from flask_login import login_required, current_user
from flask import session
import json
import zipfile
import shutil
import time
import pymysql
import requests
from openpyxl import Workbook

def citeste_configurare(file_path):
    with open(file_path, 'r') as file:
        config = json.load(file)
    return config

config = citeste_configurare('config.json')
mysql_config = config['mysql']

index = (5007966398,
5007966401,
5007966405,
5007966407,
5007966412,
5007966417,
5007992633,
5007992634)

def descarcarepdf(idSelectate):
    
    connection = pymysql.connect(
        host=mysql_config['host'],
        user=mysql_config['user'],
        password=mysql_config['password'],
        database=mysql_config['database']
    )
    cursor = connection.cursor() 
    
    print(idSelectate, 'ASTEA AICI SUNT IN STOCARE.PY')
    downlXMLbaza = 'C:/Dezvoltare/E-Factura/2023/eFactura/Ferro/eFacturaFerro local/download pdf baza de date'
    destinatie = "C:/Dezvoltare/E-Factura/2023/eFactura/Ferro/eFacturaFerro local/destinatie/"
    # downlPDFbaza = '/home/efactura/efactura_ferro/downloadPdfBazaDate'
    # destinatie = '/home/efactura/efactura_ferro/destinatie/'
    idSelectate=idSelectate[1:]

    stringID=""
    for i in range(0, len(idSelectate)):
        if i == len(idSelectate)-1:
            stringID=stringID + str(idSelectate[i])
        else:
            stringID=stringID + str(idSelectate[i]) +  ','
    print(stringID, ' STRINGID')
    file_extension =('.pdf', '.xml')
    def stergeFisiere(directory_path, file_extension):
        
        try:
            for filename in os.listdir(directory_path):
                file_path = os.path.join(directory_path, filename)
                if filename.endswith(file_extension):
                    os.remove(file_path)
                    print(f"Fisierul {filename} a fost sters.")
        except Exception as e:
            print(f"Eroare la stergerea fișierelor: {str(e)}")

    stergeFisiere(downlXMLbaza, file_extension)
    
    def make_archive(source, destination):
        base = os.path.basename(destination)
        name = base.split('.')[0]
        format = base.split('.')[1]
        archive_from = os.path.dirname(source)
        archive_to = os.path.basename(source.strip(os.sep))
        shutil.make_archive(name, format, archive_from, archive_to)
        shutil.move('%s.%s'%(name,format), destination)

    try:
        query = "SELECT nume_fisier, continut FROM tabelaFisierepdf WHERE nume_fisier IN ("+str(stringID)+")"
        print(query)
        cursor.execute(query)
        for (nume_fisier, continut) in cursor:
            cale_fisier = os.path.join(downlXMLbaza, str(nume_fisier) + '.xml')

            with open(cale_fisier, 'wb') as file:
                file.write(continut)


        def conversie():
                # xmlANAF = 'C:/Dezvoltare/E-Factura/2023/eFactura/Expeditors/eFacturaExpeditors local/output conversie'
                cale_fisier = 'C:/Dezvoltare/E-Factura/2023/eFactura/Ferro/eFacturaFerro local/download pdf baza de date'
                headerss = {"Content-Type": "text/plain"}

                # Creează un nou workbook Excel
                # workbook = Workbook()
                # sheet = workbook.active
                # sheet.title = 'Excepții'

                # Adaugă un antet pentru coloana INDEX_INCARCARE
                # sheet['A1'] = 'INDEX_INCARCARE'

                for filename in os.listdir(cale_fisier):
                    try:
                        if filename.endswith('.xml'):
                            xml_file_path = os.path.join(cale_fisier, filename)

                            with open(xml_file_path, 'rb') as xml_file:
                                xml_data = xml_file.read()

                            if 'CreditNote' in str(xml_data):
                                convert = 'https://webservicesp.anaf.ro/prod/FCTEL/rest/transformare/FCN/DA'
                            else:
                                convert = 'https://webservicesp.anaf.ro/prod/FCTEL/rest/transformare/FACT1/DA'

                            start_time = time.time()  # Momentul de start al procesării
        
                            response = None  # Inițializăm răspunsul cu None
                            max_retry_time = 16  # Numărul maxim de secunde pentru a efectua încercările
                            retry_interval = 3  # Intervalul de timp între încercări
                            
                            # Loop până când obținem un răspuns sau până când timpul maxim a fost depășit
                            while response is None and time.time() - start_time < max_retry_time:
                                try:
                                    response = requests.post(convert, data=xml_data, headers=headerss, timeout=30)
                                    # print(response.text)
                                except requests.exceptions.Timeout:
                                    # Dacă întâlnim un timeout, continuăm loop-ul și încercăm din nou
                                    pass
                                
                                # yield "\r\n"
        
                            # Așteaptă intervalul de timp specificat între încercări
                            time.sleep(retry_interval)

                            if response and response.status_code == 200:
                                filename_no_extension = os.path.splitext(filename)[0]
                                with open(f'C:/Dezvoltare/E-Factura/2023/eFactura/Ferro/eFacturaFerro local/download pdf baza de date/{filename_no_extension}.pdf', 'wb') as file:
                                    # file.write(response.content)
                                    print(f'Fisierul {filename} a fost convertit cu succes')
                            else:
                                print("Eroare la efectuarea cererii HTTP:", response.status_code)
                                print(response.text)

                            # Adaugă numele fișierului în coloana INDEX_INCARCARE
                            # sheet.append([filename_no_extension])
                    except Exception as e:
                        print("A apărut o excepție la", filename, ":", str(e))
                        # Adaugă numele fișierului în coloana INDEX_INCARCARE pentru a înregistra excepția
                        # sheet.append([filename])
                # Salvează workbook-ul Excel
                # workbook.save('C:/Dezvoltare/E-Factura/2023/eFactura/Expeditors/eFacturaExpeditors local/output conversie PDF/excepții.xlsx')

            
        conversie()
        # time.sleep(5)

        print('aici facem conversia in PDF')        
        # make_archive(downlPDFbaza, 'C:\\Dezvoltare\\E-Factura\\2023\\eFactura\\Ferro\\eFacturaFerro\\destinatie\\'+'rezultat.zip')
        # sqlSafeUpdates="set sql_safe_updates = 0"
        # cursor.execute(sqlSafeUpdates)
        # update_query = "UPDATE trimiterefacturi SET descarcata = 'Da' WHERE index_incarcare IN (" + stringID + ")"
        # print(update_query, '-------------------------------------')
        # cursor.execute(update_query)
        make_archive(downlXMLbaza, destinatie + 'rezultat.zip')
        
    except:
        print("nu are valori")

    cursor.close()
descarcarepdf(index)