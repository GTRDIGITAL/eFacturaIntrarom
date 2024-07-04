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



def conversie():
        output_directory = 'C:/Dezvoltare/E-Factura/2023/eFactura/Ferro/eFacturaFerro local/output conversie'
        headerss = {"Content-Type": "text/plain"}

        # Creează un nou workbook Excel
        workbook = Workbook()
        sheet = workbook.active
        sheet.title = 'Excepții'

        # Adaugă un antet pentru coloana INDEX_INCARCARE
        sheet['A1'] = 'INDEX_INCARCARE'

        for filename in os.listdir(output_directory):
            try:
                if filename.endswith('.xml'):
                    xml_file_path = os.path.join(output_directory, filename)

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
                            print(response.text)
                        except requests.exceptions.Timeout:
                            # Dacă întâlnim un timeout, continuăm loop-ul și încercăm din nou
                            pass
                        
                        yield "\r\n"
 
                    # Așteaptă intervalul de timp specificat între încercări
                    time.sleep(retry_interval)

                    if response and response.status_code == 200:
                        filename_no_extension = os.path.splitext(filename)[0]
                        with open(f'C:/Dezvoltare/E-Factura/2023/eFactura/Ferro/eFacturaFerro local/output conversie PDF/{filename_no_extension}.pdf', 'wb') as file:
                            file.write(response.content)
                            print(f'Fisierul {filename} a fost convertit cu succes')
                    else:
                        print("Eroare la efectuarea cererii HTTP:", response.status_code)
                        print(response.text)

                    # Adaugă numele fișierului în coloana INDEX_INCARCARE
                    # sheet.append([filename_no_extension])
            except Exception as e:
                print("A apărut o excepție la", filename, ":", str(e))
                # Adaugă numele fișierului în coloana INDEX_INCARCARE pentru a înregistra excepția
                sheet.append([filename])
        # Salvează workbook-ul Excel
        # workbook.save('C:/Dezvoltare/E-Factura/2023/eFactura/Expeditors/eFacturaExpeditors local/output conversie PDF/excepții.xlsx')

    
conversie()

print('aici facem conversia in PDF')