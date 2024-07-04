# import mysql.connector
import datetime
import os
from flask_login import login_required, current_user
from flask import session, send_from_directory
import json
import zipfile
import shutil
import time
import pymysql
import requests
import xml.etree.ElementTree as ET


def citeste_configurare(file_path):
    with open(file_path, 'r') as file:
        config = json.load(file)
    return config

config = citeste_configurare('config.json')
mysql_config = config['mysql']
dateFirma = config['dateFirma']
headers = {'Authorization': dateFirma['header']}
# Conectează-te la noua bază de date

timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
print(timestamp)
# Creează tabela pentru dict1


listaFactt = []

def stocareDictionarFacturi(data):
    
    connection = pymysql.connect(
        host=mysql_config['host'],
        user=mysql_config['user'],
        password=mysql_config['password'],
        database=mysql_config['database']
    )

    try:
        cursor = connection.cursor()
        
        dictionarFacturi = data
        data_trimis = datetime.datetime.now()
        for item in dictionarFacturi["mesaje"]:
            print(item["Factura"], item["Index"])
            factura = item["Factura"]
            index_solicitare = item["Index"]
            
            user_id = current_user.id
            
            insert_query = "INSERT ignore INTO trimiterefacturi (factura, index_incarcare, data_trimis, user_id) VALUES (%s, %s, %s, %s)"
            values = (factura, index_solicitare, data_trimis, user_id)

            cursor.execute(insert_query, values)
        connection.commit()
    except Exception as e:
        print(f"Eroare la inserare: {e}")
    finally:
        cursor.close()    
    # mydb.close()
    


def stocareMesajeAnaf(data):
    
    connection = pymysql.connect(
        host=mysql_config['host'],
        user=mysql_config['user'],
        password=mysql_config['password'],
        database=mysql_config['database']
    )

    cursor = connection.cursor()
    # Adaugă datele în tabela dict2
    dict2 = data
    for item in dict2["mesaje"]:
        data_creare = item["data_creare"]
        cif = item["cif"]
        id_solicitare = str(item["id_solicitare"])
        detalii = item["detalii"]
        tip = item["tip"]
        id_factura = item["id"]
 
        insert_query = "INSERT IGNORE INTO statusMesaje (data_creare, cif, id_solicitare, detalii, tip, id_factura) VALUES (%s, %s, %s, %s, %s, %s)"
        values = (data_creare, cif, id_solicitare, detalii, tip, id_factura)
 
        cursor.execute(insert_query, values)
        
 
    connection.commit()
    
 
    # Interogare pentru a citi din nou datele actualizate
    select_query = "SELECT * FROM statusMesaje"
    cursor.execute(select_query)
    updated_results = cursor.fetchall()
    print("updated results ", updated_results)
    cursor.close()
    
def stocareMesajeAnafPrimite(data):
    
    connection = pymysql.connect(
        host=mysql_config['host'],
        user=mysql_config['user'],
        password=mysql_config['password'],
        database=mysql_config['database']
    )

    cursor = connection.cursor()
    # Adaugă datele în tabela dict2
    dict2 = data
    for item in dict2["mesaje"]:
        if item["tip"] == "FACTURA PRIMITA":
            data_creare = item["data_creare"]
            cif = item["cif"]
            id_solicitare = str(item["id_solicitare"])
            detalii = item["detalii"]
            tip = item["tip"]
            id_factura = item["id"]

            insert_query = "INSERT IGNORE INTO statusMesaje (data_creare, cif, id_solicitare, detalii, tip, id_factura) VALUES (%s, %s, %s, %s, %s, %s)"
            values = (data_creare, cif, id_solicitare, detalii, tip, id_factura)

            cursor.execute(insert_query, values)
        
 
    connection.commit()
    
 
    # Interogare pentru a citi din nou datele actualizate
    select_query = "SELECT * FROM statusMesaje"
    cursor.execute(select_query)
    updated_results = cursor.fetchall()
    print("updated results ", updated_results)
    cursor.close()
    
    
# def stocareMesajeAnaf2(data):
    
#     connection = pymysql.connect(
#         host=mysql_config['host'],
#         user=mysql_config['user'],
#         password=mysql_config['password'],
#         database=mysql_config['database']
#     )

#     cursor = connection.cursor()
#     # Adaugă datele în tabela dict2
#     dict2 = data
#     for item in dict2["mesaje"]:
#         data_creare = item["data_creare"]
#         cif = item["cif"]
#         id_solicitare = str(item["id_solicitare"])
#         detalii = item["detalii"]
#         tip = item["tip"]
#         id_factura = item["id"]
 
#         insert_query = "INSERT IGNORE INTO statusMesaje2 (data_creare, cif, id_solicitare, detalii, tip, id_factura) VALUES (%s, %s, %s, %s, %s, %s)"
#         values = (data_creare, cif, id_solicitare, detalii, tip, id_factura)
 
#         cursor.execute(insert_query, values)
        
 
#     connection.commit()
    
 
#     # Interogare pentru a citi din nou datele actualizate
#     select_query = "SELECT * FROM statusMesaje"
#     cursor.execute(select_query)
#     updated_results = cursor.fetchall()
#     # print("updated results ", updated_results)
#     cursor.close()


# def interogareTabela():
#     connection = pymysql.connect(
#         host=mysql_config['host'],
#         user=mysql_config['user'],
#         password=mysql_config['password'],
#         database=mysql_config['database']
#     )
#     cursor = connection.cursor()
    
#     selectQuery = "SELECT distinct * FROM JOINDATE WHERE tip IN('ERORI FACTURA', 'FACTURA TRIMISA')"
#     cursor.execute(selectQuery)

#     results = []

#     for row in cursor.fetchall():
#         if 'ERORI' in row[5]:
#             descarcata = 'Nu'
#         else:
#             descarcata = row[8]
        
#         result_dict = {
#             "factura": row[0],
#             "data_creare": row[1],
#             "cif": row[2],
#             "id_solicitare": row[3],
#             "detalii": row[4],
#             "tip": row[5],
#             "id_factura": row[6],
#             "user_id": row[7],
#             "descarcata": descarcata  
#         }
#         results.append(result_dict)
#     cursor.close()

#     return results


def interogareTabelaPrimite():
    
    connection = pymysql.connect(
        host=mysql_config['host'],
        user=mysql_config['user'],
        password=mysql_config['password'],
        database=mysql_config['database']
    )
    cursor = connection.cursor()
    
    # selectQuery = "SELECT distinct * FROM statusmesaje WHERE tip ='FACTURA PRIMITA'"
    selectQuery = "SELECT distinct * FROM facturiPrimite"
    cursor.execute(selectQuery)

    results = []

    for row in cursor.fetchall():
        result_dict = {
            "factura": row[7],
            "furnizor": row[8],
            "data_creare": row[0],
            "cif": row[1],
            "id_solicitare": row[2],
            "detalii": row[3],
            "tip": row[4],
            "id_factura": row[5],
            "descarcata": row[6]
        }
    
        results.append(result_dict)
        print('REZULTATE ', results)
    cursor.close()
    
    return results

def interogareFisierePDFPrimite():
    
    connection = pymysql.connect(
        host=mysql_config['host'],
        user=mysql_config['user'],
        password=mysql_config['password'],
        database=mysql_config['database']
    )
    cursor = connection.cursor()
    
    selectQuery = "SELECT distinct nume_fisier FROM fisierepdf"
    cursor.execute(selectQuery)
    
    listaPrimite =[]
    for row in cursor.fetchall():
        listaPrimite.append(row)
    listaPrimite = [factura[0] for factura in listaPrimite]
    # print("FACTURI PRIMITE ", listaPrimite)
    return listaPrimite

def numarFacturiTrimise():
    connection = pymysql.connect(
        host=mysql_config['host'],
        user=mysql_config['user'],
        password=mysql_config['password'],
        database=mysql_config['database']
    )
    cursor = connection.cursor()
    
    numarFact = "SELECT COUNT(*) AS numar_facturi FROM trimiterefacturi GROUP BY data_trimis HAVING COUNT(*) > 1 ORDER BY data_trimis DESC limit 1"
    cursor.execute(numarFact)
    resultNrFact = cursor.fetchall()
    resultNrFactList = [row[0] for row in resultNrFact]
    cursor.close()
    
    return resultNrFactList

nrFactTrimise = numarFacturiTrimise()
print("NUMARUL DE FACTURI TRIMISE ", nrFactTrimise)

def nrFacturiIstoric():
    
    connection = pymysql.connect(
        host=mysql_config['host'],
        user=mysql_config['user'],
        password=mysql_config['password'],
        database=mysql_config['database']
    )
    cursor = connection.cursor()
    
    numarFacturiTrimiseIstoric =  "select count(*) from trimiterefacturi"
    cursor.execute(numarFacturiTrimiseIstoric)
    resultIstoric = cursor.fetchall()
    cursor.close()
    
    return resultIstoric

# print(nrFacturiIstoric())
    

def listaFacturi(data):
    
    connection = pymysql.connect(
        host=mysql_config['host'],
        user=mysql_config['user'],
        password=mysql_config['password'],
        database=mysql_config['database']
    )
    cursor = connection.cursor()
    
    selectQueryFacturi = f"SELECT index_incarcare FROM trimiterefacturi order by data_trimis desc limit {data}"
    cursor.execute(selectQueryFacturi)

    result = cursor.fetchall()
    result_list = [row[0] for row in result]
    
    cursor.close()

    return result_list

for i in nrFactTrimise:
    listaFactt=listaFacturi(i)
print("asta e listaaaa ",listaFactt)
print("aici e numaruuuul ", len(listaFactt))
# print(aba)

def stocarePDF():
    
    connection = pymysql.connect(
        host=mysql_config['host'],
        user=mysql_config['user'],
        password=mysql_config['password'],
        database=mysql_config['database']
    )
    cursor = connection.cursor()
    
    director_fisiere = "C:/Dezvoltare/E-Factura/2023/eFactura/Intrarom/Intrarom local/output conversie"
    # director_fisiere = '/home/efactura/efactura_intrarom/outputConversie/'

# Parcurgerea fișierelor din director și inserarea în baza de date
    for nume_fisier in os.listdir(director_fisiere):
        if nume_fisier.endswith('.xml'):
            cale_absoluta = os.path.join(director_fisiere, nume_fisier)
            
            with open(cale_absoluta, 'rb') as file:
                pdf_content = file.read()
            nume_fisier=nume_fisier.replace(".xml", "")
            
            

            insert_query = "INSERT INTO FisierePDF (nume_fisier, continut, data_introducere) VALUES (%s, %s, %s)"
            values = (nume_fisier, pdf_content, timestamp)
            cursor.execute(insert_query, values)
    connection.commit()
    cursor.close()
    
def stocarePDFPrimite():
    
    connection = pymysql.connect(
        host=mysql_config['host'],
        user=mysql_config['user'],
        password=mysql_config['password'],
        database=mysql_config['database']
    )
    cursor = connection.cursor()
    
    director_fisiere = "C:/Dezvoltare/E-Factura/2023/eFactura/Intrarom/Intrarom local/output conversie"
    # director_fisiere = '/home/efactura/efactura_intrarom/outputConversie/'
    for nume_fisier in os.listdir(director_fisiere):
        if nume_fisier.endswith('.xml'):
            cale_absoluta = os.path.join(director_fisiere, nume_fisier)
            
            with open(cale_absoluta, 'rb') as file:
                pdf_content = file.read()
            nume_fisier=nume_fisier.replace(".xml", "")
            tree = ET.parse(cale_absoluta)
            root = tree.getroot()
            namespaces = {
                    'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
                    'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2'
                }
            numar_factura_element = root.find('.//cbc:ID', namespaces)
            data_factura_element = root.find('.//cbc:IssueDate', namespaces)
            if numar_factura_element is not None:
                numar_factura = numar_factura_element.text
                print('aici avem numarul facturii', numar_factura)
            else:
                print(f"Elementul ID nu a fost găsit în fișierul {nume_fisier}.xml")
                continue
            
            if data_factura_element is not None:
                data_factura = data_factura_element.text
                print('aici avem numarul facturii', numar_factura)
            else:
                print(f"Elementul ID nu a fost găsit în fișierul {nume_fisier}.xml")
                continue
            
            nume_furnizor_element = root.find('.//cac:PartyLegalEntity/cbc:RegistrationName', namespaces)
            if nume_furnizor_element is not None:
                nume_furnizor = nume_furnizor_element.text
                print(f'Numele furnizorului din fișierul {nume_fisier}: {nume_furnizor}')
            else:
                print(f'Nu am putut găsi numele furnizorului în fișierul {nume_fisier}')
            

            insert_query = "INSERT INTO FisierePDFPrimite (nume_fisier, numar_factura, nume_furnizor, continut, data_introducere, data_factura) VALUES (%s, %s, %s, %s, %s, %s)"
            values = (nume_fisier, numar_factura, nume_furnizor, pdf_content, timestamp, data_factura)
            cursor.execute(insert_query, values)
    connection.commit()
    cursor.close()
# Parcurgerea fișierelor din director și inserarea în baza de date
    # for nume_fisier in os.listdir(director_fisiere):
    #     if nume_fisier.endswith('.xml'):
    #         cale_absoluta = os.path.join(director_fisiere, nume_fisier)
            
    #         with open(cale_absoluta, 'rb') as file:
    #             pdf_content = file.read()
    #         nume_fisier=nume_fisier.replace(".xml", "")
    #         tree = ET.parse(cale_absoluta)
    #         root = tree.getroot()

    #         numar_factura_element = root.find('.//cbc:ID', namespaces)
    #         if numar_factura_element is not None:
    #             numar_factura = numar_factura_element.text
    #             print('aici avem numarul facturii', numar_factura)
    #         else:
    #             print(f"Elementul ID nu a fost găsit în fișierul {nume_fisier}.xml")
    #             continue
            
    #         nume_furnizor_element = root.find('.//cac:PartyLegalEntity/cbc:RegistrationName', namespaces)
    #         if nume_furnizor_element is not None:
    #             nume_furnizor = nume_furnizor_element.text
    #             print(f'Numele furnizorului din fișierul {nume_fisier}: {nume_furnizor}')
    #         else:
    #             print(f'Nu am putut găsi numele furnizorului în fișierul {nume_fisier}')
            

    #         insert_query = "INSERT INTO FisierePDFPrimite (nume_fisier, numar_factura, nume_furnizor, continut, data_introducere) VALUES (%s, %s, %s, %s, %s)"
    #         values = (nume_fisier, numar_factura, nume_furnizor, pdf_content, timestamp)
    #         cursor.execute(insert_query, values)
    # connection.commit()
    # cursor.close()


def descarcarepdf(idSelectate):
    
    connection = pymysql.connect(
        host=mysql_config['host'],
        user=mysql_config['user'],
        password=mysql_config['password'],
        database=mysql_config['database']
    )
    cursor = connection.cursor() 
    
    # print(idSelectate, 'ASTEA AICI SUNT IN STOCARE.PY')
    downlXMLbaza = 'C:/Dezvoltare/E-Factura/2023/eFactura/Intrarom/Intrarom local/download pdf baza de date'
    destinatie = "C:/Dezvoltare/E-Factura/2023/eFactura/Intrarom/Intrarom local/destinatie/"
    # downlXMLbaza = '/home/efactura/efactura_intrarom/downloadPdfBazaDate'
    # destinatie = '/home/efactura/efactura_intrarom/destinatie/'
    # idSelectate=idSelectate[1:]
    print(idSelectate, 'ASTEA SUNT SELECTATE')
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
        query = "SELECT nume_fisier, continut FROM fisierepdf WHERE nume_fisier IN ("+str(stringID)+")"
        print(query)
        cursor.execute(query)
        # print("ce plm ai")
        for (nume_fisier, continut) in cursor:
            cale_fisier = os.path.join(downlXMLbaza, str(nume_fisier) + '.xml')
            print(f"am gasit {stringID}")

            with open(cale_fisier, 'wb') as file:
                file.write(continut)
        print(stringID, 'STRINGGGGGGGGG')


        def conversie():
                # xmlANAF = 'C:/Dezvoltare/E-Factura/2023/eFactura/Expeditors/eFacturaExpeditors local2/output conversie'
                cale_fisier = '/download pdf baza de date'
                # cale_fisier = '/home/efactura/efactura_intrarom/downloadPdfBazaDate'
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
                                with open(f'C:/Dezvoltare/E-Factura/2023/eFactura/Intrarom/Intrarom local/download pdf baza de date/{filename_no_extension}.pdf', 'wb') as file:
                                # with open(f'/home/efactura/efactura_intrarom/downloadPdfBazaDate/{filename_no_extension}.pdf', 'wb') as file:
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
                        # sheet.append([filename])
                # Salvează workbook-ul Excel
                # workbook.save('C:/Dezvoltare/E-Factura/2023/eFactura/Expeditors/eFacturaExpeditors local2/output conversie PDF/excepții.xlsx')

            
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

def stergeFisiere(directory_path, file_extension):
        
    try:
        for filename in os.listdir(directory_path):
            file_path = os.path.join(directory_path, filename)
            if filename.endswith(file_extension):
                os.remove(file_path)
                print(f"Fisierul {filename} a fost sters.")
    except Exception as e:
        print(f"Eroare la stergerea fișierelor: {str(e)}")

def descarcarepdfPrimite(idSelectate):
    # Configurație pentru conexiunea la baza de date
    connection = pymysql.connect(
        host=mysql_config['host'],
        user=mysql_config['user'],
        password=mysql_config['password'],
        database=mysql_config['database']
    )
    cursor = connection.cursor() 
    
    print(idSelectate, 'ASTEA AICI SUNT IN STOCARE.PY')
    
    downlXMLbaza = 'C:/Dezvoltare/E-Factura/2023/eFactura/Intrarom/Intrarom local/download pdf baza de date'
    destinatie = "C:/Dezvoltare/E-Factura/2023/eFactura/Intrarom/Intrarom local/destinatie/"
    
    # Eliminăm primul element din lista idSelectate
    idSelectate = idSelectate[1:]
    
    # Creăm un string ID pentru query-ul SQL
    stringID = ",".join(map(str, idSelectate))
    print(stringID, ' STRINGID')
    
    # Extensia fișierelor de șters
    file_extension = ('.pdf', '.xml')
    
    # Funcție pentru ștergerea fișierelor dintr-un director specific
    def stergeFisiere(downlXMLbaza, file_extension):
        for root, dirs, files in os.walk(downlXMLbaza):
            for file in files:
                if file.endswith(file_extension):
                    os.remove(os.path.join(root, file))
    
    # Ștergem fișierele din directorul specificat
    stergeFisiere(downlXMLbaza, file_extension)
    
    # Funcție pentru crearea unui arhiv ZIP
    def make_archive(source, destination):
        base = os.path.basename(destination)
        name = base.split('.')[0]
        format = base.split('.')[1]
        archive_from = os.path.dirname(source)
        archive_to = os.path.basename(source.strip(os.sep))
        shutil.make_archive(name, format, archive_from, archive_to)
        shutil.move('%s.%s' % (name, format), destination)

    try:
        query = f"SELECT nume_fisier, data_factura, numar_factura, nume_furnizor, continut FROM fisierepdfprimite WHERE nume_fisier IN ({stringID})"
        print("Query:", query)
        
        cursor.execute(query)
        print("Query executat cu succes")

        for (nume_fisier, data_factura, numar_factura, nume_furnizor, continut) in cursor:
            cale_fisier = os.path.join(downlXMLbaza, f"{numar_factura} {data_factura} {nume_furnizor}.xml")
            print(f"Scriem fișierul: {cale_fisier}")
            
            with open(cale_fisier, 'wb') as file:
                file.write(continut)
                print(f"Fișier salvat la: {cale_fisier}")

        def conversie():
            cale_fisier = 'C:/Dezvoltare/E-Factura/2023/eFactura/Intrarom/Intrarom local/download pdf baza de date'
            headerss = {"Content-Type": "text/plain"}

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
                            except requests.exceptions.Timeout:
                                # Dacă întâlnim un timeout, continuăm loop-ul și încercăm din nou
                                pass
                            time.sleep(retry_interval)

                        if response and response.status_code == 200:
                            filename_no_extension = os.path.splitext(filename)[0]
                            pdf_path = os.path.join(cale_fisier, f"{filename_no_extension}.pdf")
                            with open(pdf_path, 'wb') as file:
                                file.write(response.content)
                                print(f'Fișierul {filename} a fost convertit cu succes în {pdf_path}')
                        else:
                            print("Eroare la efectuarea cererii HTTP:", response.status_code)
                            if response:
                                print(response.text)
                except Exception as e:
                    print("A apărut o excepție la", filename, ":", str(e))

        conversie()

        if stringID:
            try:
                sqlSafeUpdates = "SET sql_safe_updates = 0"
                cursor.execute(sqlSafeUpdates)
                
                update_query = f"UPDATE statusmesaje SET descarcata = 'Da' WHERE id_solicitare IN ({stringID})"
                print(update_query, '-------------------------------------')
                cursor.execute(update_query)
                
                connection.commit()  # Commit the transaction
            except Exception as e:
                print(f"An error occurred: {e}")
            finally:
                cursor.close()
                connection.close()
        else:
            print("No IDs provided to update.")

        make_archive(downlXMLbaza, destinatie + 'rezultat.zip')
        
    except Exception as e:
        print(f"Eroare în blocul principal: {e}")

    cursor.close()
    
def interogareTabelaClienti():
    
    connection = pymysql.connect(
        host=mysql_config['host'],
        user=mysql_config['user'],
        password=mysql_config['password'],
        database=mysql_config['database']
    )
    cursor = connection.cursor()
    
    resultsclienti=[]
    # selectQuery = "SELECT * FROM CLIENTS where country in ('RO', 'România')"
    selectQuery = "SELECT * FROM CLIENTS where country not in ('RO', 'România')"
    cursor.execute(selectQuery)
 
    resultsclienti = []
 
    for row in cursor.fetchall():
        result_dict = {
            "id":row[0],
            "name": row[1],
            "country": row[2],
            "cust": row[3],
            "regno": row[4],
            "city": row[5],
            "street": row[6],
            "region": row[8],
        }
        resultsclienti.append(result_dict)
        
        cursor.close()
        # print(resultsclienti)
 
    return resultsclienti


# def interogareTabelaClienti10():
    
#     connection = pymysql.connect(
#         host=mysql_config['host'],
#         user=mysql_config['user'],
#         password=mysql_config['password'],
#         database=mysql_config['database']
#     )
#     cursor = connection.cursor()
    
#     resultsclienti=[]
#     # selectQuery = "SELECT * FROM CLIENTS where country in ('RO', 'România')"
#     selectQuery = "SELECT * FROM CLIENTS where country not in ('RO', 'România')"
#     cursor.execute(selectQuery)
 
#     resultsclienti = []
 
#     for row in cursor.fetchall():
#         result_dict = {
#             "id":row[0],
#             "name": row[1],
#             "country": row[2],
#             "cust": row[3],
#             "regno": row[4],
#             "city": row[5],
#             "street": row[6],
#             "region": row[8],
#         }
#         resultsclienti.append(result_dict)
#         # print(resultsclienti)
#         cursor.close()
 
#     return resultsclienti


def interogareIDprimite():
    connection = pymysql.connect(
        host=mysql_config['host'],
        user=mysql_config['user'],
        password=mysql_config['password'],
        database=mysql_config['database']
    )
    cursor = connection.cursor()
    
    selectQuery = "SELECT distinct id_factura FROM statusmesaje WHERE tip ='FACTURA PRIMITA'"
    cursor.execute(selectQuery)
    result_list = [row[0] for row in cursor.fetchall()]
    cursor.close()
    connection.close()
    return result_list



def interogareTabelaFacturiTrimise():
    connection = pymysql.connect(
        host=mysql_config['host'],
        user=mysql_config['user'],
        password=mysql_config['password'],
        database=mysql_config['database']
    )
    cursor = connection.cursor()
    
    selectQuery = "SELECT distinct * FROM trimiterefacturi"
    cursor.execute(selectQuery)

    results = []

    for row in cursor.fetchall():
        
        result_dict = {
            "factura": row[1],
            "index_incarcare": row[2],
            "data_trimis": row[3],
            "status_facturi": row[6],
            "user_id": row[4],
            "descarcata": row[5]  
        }
        results.append(result_dict)
    cursor.close()

    return results

def interogareIndexIncarcare():
    connection = pymysql.connect(
        host=mysql_config['host'],
        user=mysql_config['user'],
        password=mysql_config['password'],
        database=mysql_config['database']
    )
    cursor = connection.cursor()
    
    # selectQuery = "SELECT index_incarcare FROM trimiterefacturi where status_facturi ='' or status_facturi like '%prelucrare';"
    selectQuery = "SELECT index_incarcare FROM trimiterefacturi where status_facturi ='' or status_facturi like '%prelucrare%';"
    cursor.execute(selectQuery)

    results = [int(row[0]) for row in cursor.fetchall()]  # Extracting only the first element from each row
    
    cursor.close()

    return results

def stareMesaj(results):
    connection = pymysql.connect(
        host=mysql_config['host'],
        user=mysql_config['user'],
        password=mysql_config['password'],
        database=mysql_config['database']
    )
    cursor = connection.cursor()
    
    for i in range(0, len(results)):
        try:
            if str(results[i])[:1] == '5':
                apiStareMesaj = 'https://api.anaf.ro/prod/FCTEL/rest/stareMesaj?id_incarcare='+str(results[i])
            else:
                apiStareMesaj = 'https://api.anaf.ro/prod/FCTEL/rest/stareMesaj?id_incarcare='+str(results[i])
                
            print(apiStareMesaj)
            # while True:  # buclă infinită
            stare = requests.get(apiStareMesaj, headers=headers, timeout=30)
            if stare.status_code == 200:
                resp = stare.text
                print('RESP ',resp)
                root = ET.fromstring(resp)
                staree = str(root.attrib['stare'])
                
                updateQuery = f'update trimiterefacturi set status_facturi = "{staree}" where index_incarcare = {results[i]}'
                print(updateQuery)
                cursor.execute(updateQuery)
                connection.commit()
            print(results[i])
        except:
            print("eroare la ", results[i])
    
            

def statusStareMesajBD():
    connection = pymysql.connect(
        host=mysql_config['host'],
        user=mysql_config['user'],
        password=mysql_config['password'],
        database=mysql_config['database']
    )

    cursor = connection.cursor()
        
    dictionarFacturi = interogareIndexIncarcare()
    print(dictionarFacturi)
    stareMesaj(dictionarFacturi)
    cursor.close()    

def updateFacturi(stringID):
    try:
        connection = pymysql.connect(
            host=mysql_config['host'],
            user=mysql_config['user'],
            password=mysql_config['password'],
            database=mysql_config['database']
        )
        
        cursor = connection.cursor()
        sqlSafeUpdates="SET sql_safe_updates = 0"
        cursor.execute(sqlSafeUpdates)
        
        for i in stringID:
            update_query = f"UPDATE trimiterefacturi SET descarcata = 'Da' WHERE index_incarcare = {i}"
            cursor.execute(update_query)
            print(update_query, '-------------------------------------')
            
        connection.commit()  # Commit pentru a salva schimbările în baza de date
        
    except Exception as e:
        print(f"An error occurred: {e}")
        
    finally:
        if 'connection' in locals() and connection.open:
            cursor.close()
            connection.close() 
    
def raspunsANAF(id_selectate):
        # --------------------------------STARE MESAj -----------------------------------
    # try:
        stergeFisiere('C:/Dezvoltare/E-Factura/2023/eFactura/Intrarom/Intrarom local/output zip api', '.zip')
        listaIdDescarcare = []
        string_value = id_selectate[0]

        # Split șirul de caractere folosind virgula ca separator
        string_list = string_value.split(',')

        # Convertește fiecare element la int
        number_list = [int(x) for x in string_list]

        print(number_list)
        # print(id_selectate)
        def stareMesaj():
            listaIdDescarcare.clear()
            for i in range(0, len(number_list)):
                print('in for ',number_list[i])
                apiStareMesaj = 'https://api.anaf.ro/prod/FCTEL/rest/stareMesaj?id_incarcare='+str(number_list[i])
                
                while True:  # buclă infinită
                    stare = requests.get(apiStareMesaj, headers=headers, timeout=30)
                    if stare.status_code == 200:
                        resp = stare.text
                        root = ET.fromstring(resp)
                        print(resp)
                        staree = str(root.attrib['stare'])
                        if staree != 'in prelucrare':  # dacă starea nu mai este 'in prelucrare', se iese din buclă
                            break
                        time.sleep(5)  # așteaptă 5 secunde înainte de a interoga din nou API-ul
                    else:
                        print('Eroare la interogarea API-ului')
                        break  # dacă există o eroare la interogarea API-ului, se iese din buclă

                try:
                    id_descarcare = int(root.attrib['id_descarcare']) 
                    listaIdDescarcare.append(id_descarcare)
                    # print('id descarcare',id_descarcare, id_selectate[i])   
                except:
                    print(resp) 
        # print("aici am facut starea mesajului")                 
        stareMesaj()
        print(listaIdDescarcare)



        # --------------------- DESCARCARE -------------------
        time.sleep(10)
        def descarcare():
            for i in range(0, len(listaIdDescarcare)):
                apiDescarcare = 'https://api.anaf.ro/prod/FCTEL/rest/descarcare?id='+str(listaIdDescarcare[i])

                descarcare = requests.get(apiDescarcare, headers=headers, timeout=30)

                if descarcare.status_code == 200:
                    # print("Cererea a fost efectuata cu succes!")
                    with open('C:/Dezvoltare/E-Factura/2023/eFactura/Intrarom/Intrarom local/output zip api/fisier'+str(listaIdDescarcare[i])+'.zip', 'wb') as file:
                    # with open("/home/efactura/efactura_intrarom/outputZipAPI/fisier"+str(listaIdDescarcare[i])+'.zip', 'wb') as file:
                        file.write(descarcare.content)
                        print('Descarcat cu success')
                    
                # print(descarcare.text)
                else:
                    print("Eroare la efectuarea cererii HTTP:", descarcare.status_code)
                    print(descarcare.text)
        # print("aici descarcam folosind id_descarcare")
        descarcare()

        directory_path = 'C:/Dezvoltare/E-Factura/2023/eFactura/Intrarom/Intrarom local/output zip api'
        # directory_path = "/home/efactura/efactura_intrarom/outputZipAPI"

        output_directory = 'C:/Dezvoltare/E-Factura/2023/eFactura/Intrarom/Intrarom local/output conversie'
        # output_directory = "/home/efactura/efactura_intrarom/outputConversie"
        # arhiveANAF = "/home/efactura/efactura_intrarom/arhiveANAF"

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
            
        stocarePDF()
        # stergeFisiere('/output conversie', '.xml')
        print("facem stocarea pdf")
        # print("aici stocam XML in BD")
        # for i in range(0, len(number_list)):
        #     print(number_list[i])
        #     updateFacturi(number_list[i])
        
        updateFacturi(number_list) 
        print("plmmm ", number_list)                 
        


        pdf_directory = 'C:/Dezvoltare/E-Factura/2023/eFactura/Intrarom/Intrarom local/output conversie PDF'
        # pdf_directory = '/home/efactura/efactura_intrarom/outputConversiePDF'
        # zip_file_path = '/home/efactura/efactura_intrarom/outputArhiveConversiePDF/rezultatArhiveConversie.zip'
        zip_file_path = 'C:/Dezvoltare/E-Factura/2023/eFactura/Intrarom/Intrarom local/output arhive conversie PDF/rezultatArhiveConversie.zip'
        make_archive(directory_path, os.path.join(pdf_directory, 'rezultat.zip'))   

        with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for pdf_file in os.listdir(pdf_directory):
                pdf_file_path = os.path.join(pdf_directory, pdf_file)
                zip_file.write(pdf_file_path, os.path.basename(pdf_file)) 
    # except:
    #     print('nu a ales nimic din lista')

def stocareZIPAnaf():
    connection = pymysql.connect(
        host=mysql_config['host'],
        user=mysql_config['user'],
        password=mysql_config['password'],
        database=mysql_config['database']
    )
    cursor = connection.cursor()
    
    director_fisiere = "C:/Dezvoltare/E-Factura/2023/eFactura/Intrarom/Intrarom local/output conversie"
    # director_fisiere = '/home/efactura/efactura_intrarom/outputConversie/'

# Parcurgerea fișierelor din director și inserarea în baza de date
    for nume_fisier in os.listdir(director_fisiere):
        if nume_fisier.endswith('.zip'):
            cale_absoluta = os.path.join(director_fisiere, nume_fisier)
            
            with open(cale_absoluta, 'rb') as file:
                pdf_content = file.read()
            nume_fisier=nume_fisier.replace(".zip", "")
            
            

            insert_query = "INSERT INTO fisierezip (nume_fisier, continut, data_introducere) VALUES (%s, %s, %s)"
            values = (nume_fisier, pdf_content, timestamp)
            cursor.execute(insert_query, values)
    connection.commit()
    cursor.close()
    # filename = 'rezultatArhiveConversie.zip'
    # return send_from_directory('/output arhive conversie PDF', filename, as_attachment = True)