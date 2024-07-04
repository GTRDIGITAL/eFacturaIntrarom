# import mysql.connector
import datetime
import os
from flask_login import login_required, current_user
from flask import session
import json
import zipfile
import shutil
import time
import pymysql

def citeste_configurare(file_path):
    with open(file_path, 'r') as file:
        config = json.load(file)
    return config

config = citeste_configurare('config.json')
mysql_config = config['mysql']

# Conectează-te la noua bază de date
mydb = pymysql.connect(
    host=mysql_config['host'],
    user=mysql_config['user'],
    password=mysql_config['password'],
    database=mysql_config['database']
)
timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
print(timestamp)
# Creează tabela pentru dict1
mycursor = mydb.cursor()

listaFactt = []

def stocareDictionarFacturi(data):
    dictionarFacturi = data
    data_trimis = datetime.datetime.now()
    for item in dictionarFacturi["mesaje"]:
        print(item["Factura"], item["Index"])
        factura = item["Factura"]
        index_solicitare = item["Index"]
        
        user_id = current_user.id
        
        
        insert_query = "INSERT ignore INTO trimitereFacturi (factura, index_incarcare, data_trimis, user_id) VALUES (%s, %s, %s, %s)"
        values = (factura, index_solicitare, data_trimis, user_id)

        mycursor.execute(insert_query, values)
    mydb.commit()
    # mydb.close()

def stocareMesajeAnaf(data):
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
 
        mycursor.execute(insert_query, values)
 
    mydb.commit()
 
    # Interogare pentru a citi din nou datele actualizate
    select_query = "SELECT * FROM statusMesaje"
    mycursor.execute(select_query)
    updated_results = mycursor.fetchall()
    print("updated results ", updated_results)


def interogareTabela():
    
    selectQuery = "SELECT distinct * FROM JOINDATE WHERE tip IN('ERORI FACTURA', 'FACTURA TRIMISA')"
    mycursor.execute(selectQuery)

    results = []

    for row in mycursor.fetchall():
        if 'ERORI' in row[5]:
            descarcata = 'Nu'
        else:
            descarcata = row[8]
        
        result_dict = {
            "factura": row[0],
            "data_creare": row[1],
            "cif": row[2],
            "id_solicitare": row[3],
            "detalii": row[4],
            "tip": row[5],
            "id_factura": row[6],
            "user_id": row[7],
            "descarcata": descarcata  
        }
        results.append(result_dict)

    return results

def interogareTabelaPrimite():
    
    selectQuery = "SELECT distinct * FROM JOINDATE WHERE tip ='FACTURA PRIMITA'"
    mycursor.execute(selectQuery)

    results = []

    for row in mycursor.fetchall():
        result_dict = {
            "factura": row[0],
            "data_creare": row[1],
            "cif": row[2],
            "id_solicitare": row[3],
            "detalii": row[4],
            "tip": row[5],
            "id_factura": row[6],
            "user_id": row[7],
            "descarcata": row[8]
        }
        results.append(result_dict)
        # print(results)

    return results

def numarFacturiTrimise():
    numarFact = "SELECT COUNT(*) AS numar_facturi FROM trimiterefacturi GROUP BY data_trimis HAVING COUNT(*) > 1 ORDER BY data_trimis DESC limit 1"
    mycursor.execute(numarFact)
    resultNrFact = mycursor.fetchall()
    resultNrFactList = [row[0] for row in resultNrFact]
    return resultNrFactList

nrFactTrimise = numarFacturiTrimise()
print("NUMARUL DE FACTURI TRIMISE ", nrFactTrimise)

def nrFacturiIstoric():
    numarFacturiTrimiseIstoric =  "select count(*) from trimiterefacturi"
    mycursor.execute(numarFacturiTrimiseIstoric)
    resultIstoric = mycursor.fetchall()
    return resultIstoric

# print(nrFacturiIstoric())
    

def listaFacturi(data):
    selectQueryFacturi = f"SELECT index_incarcare FROM trimiterefacturi order by data_trimis desc limit {data}"
    mycursor.execute(selectQueryFacturi)

    result = mycursor.fetchall()
    result_list = [row[0] for row in result]

    return result_list

for i in nrFactTrimise:
    listaFactt=listaFacturi(i)
print("asta e listaaaa ",listaFactt)
print("aici e numaruuuul ", len(listaFactt))
# print(aba)

def stocarePDF():
    director_fisiere = "C:/Dezvoltare/E-Factura/2023/eFactura/Ferro/eFacturaFerro local/output conversie PDF/"
    # director_fisiere = '/home/efactura/efactura_ferro/outputConversiePDF'

# Parcurgerea fișierelor din director și inserarea în baza de date
    for nume_fisier in os.listdir(director_fisiere):
        if nume_fisier.endswith('.pdf'):
            cale_absoluta = os.path.join(director_fisiere, nume_fisier)
            
            with open(cale_absoluta, 'rb') as file:
                pdf_content = file.read()
            nume_fisier=nume_fisier.replace(".pdf", "")
            
            

            insert_query = "INSERT INTO FisierePDF (nume_fisier, continut, data_introducere) VALUES (%s, %s, %s)"
            values = (nume_fisier, pdf_content, timestamp)
            mycursor.execute(insert_query, values)
    mydb.commit()


def descarcarepdf(idSelectate):
    mycursor = mydb.cursor()
    print(idSelectate, 'ASTEA AICI SUNT IN STOCARE.PY')
    downlPDFbaza = 'C:\\Dezvoltare\\E-Factura\\2023\\eFactura\\Ferro\\eFacturaFerro local\\download pdf baza de date'
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
    
    def stergeFisiere(directory_path, file_extension):
        try:
            for filename in os.listdir(directory_path):
                file_path = os.path.join(directory_path, filename)
                if filename.endswith(file_extension):
                    os.remove(file_path)
                    print(f"Fisierul {filename} a fost sters.")
        except Exception as e:
            print(f"Eroare la stergerea fișierelor: {str(e)}")

    stergeFisiere(downlPDFbaza, '.pdf')
    
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
        mycursor.execute(query)
        for (nume_fisier, continut) in mycursor:
            cale_fisier = os.path.join(downlPDFbaza, str(nume_fisier) + '.pdf')

            with open(cale_fisier, 'wb') as file:
                file.write(continut)
        # make_archive(downlPDFbaza, 'C:\\Dezvoltare\\E-Factura\\2023\\eFactura\\Ferro\\eFacturaFerro\\destinatie\\'+'rezultat.zip')
        sqlSafeUpdates="set sql_safe_updates = 0"
        mycursor.execute(sqlSafeUpdates)
        update_query = "UPDATE trimiterefacturi SET descarcata = 'Da' WHERE index_incarcare IN (" + stringID + ")"
        print(update_query, '-------------------------------------')
        mycursor.execute(update_query)
        make_archive(downlPDFbaza, destinatie + 'rezultat.zip')
        
    except:
        print("nu are valori")

    mycursor.close()


    
def interogareTabelaClienti():
    resultsclienti=[]
    # selectQuery = "SELECT * FROM CLIENTS where country in ('RO', 'România')"
    selectQuery = "SELECT * FROM CLIENTS where country not in ('RO', 'România')"
    mycursor.execute(selectQuery)
 
    resultsclienti = []
 
    for row in mycursor.fetchall():
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
        # print(resultsclienti)
 
    return resultsclienti


def interogareTabelaClienti10():
    resultsclienti=[]
    # selectQuery = "SELECT * FROM CLIENTS where country in ('RO', 'România')"
    selectQuery = "SELECT * FROM CLIENTS where country not in ('RO', 'România')"
    mycursor.execute(selectQuery)
 
    resultsclienti = []
 
    for row in mycursor.fetchall():
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
        # print(resultsclienti)
 
    return resultsclienti