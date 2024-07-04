import os
import requests
import time
import xml.etree.ElementTree as ET
import zipfile
import datetime
# import stocareBD
from .stocareBD import *
# import stocareBD
import json
from openpyxl import Workbook

def citeste_configurare(file_path):
    with open(file_path, 'r') as file:
        config = json.load(file)
    return config

config = citeste_configurare('config.json')
mysql_config = config['mysql']
dateFirma = config['dateFirma']

current_datetime = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
cif = dateFirma['cui']
headers = {'Authorization': dateFirma['header']}

# print("ASTA E header", headers)
print("hai zdreanta mea, mergi")

listaIndexIncarcare = []
listaIdDescarcare = []
listaMesajeEroare = []
facturaIndex = []
dictionarFacturi = {}
lungimeListaFacturi = []
listaTest = []
fisiere_xml = []
numarFactura=[]

def eFactura():
    def stergeFisiere(directory_path, file_extension):
        try:
            for filename in os.listdir(directory_path):
                file_path = os.path.join(directory_path, filename)
                if filename.endswith(file_extension):
                    os.remove(file_path)
                    print(f"Fisierul {filename} a fost sters.")
        except Exception as e:
            print(f"Eroare la stergerea fișierelor: {str(e)}")

    stergeFisiere('C:/Dezvoltare/E-Factura/2023/eFactura/Konica/eFacturaKonicaMinolta local/output conversie', '.xml')
    stergeFisiere('C:/Dezvoltare/E-Factura/2023/eFactura/Konica/eFacturaKonicaMinolta local/output zip api', '.zip')
    stergeFisiere('C:/Dezvoltare/E-Factura/2023/eFactura/Konica/eFacturaKonicaMinolta local/output conversie PDF', '.pdf')
    stergeFisiere('C:/Dezvoltare/E-Factura/2023/eFactura/Konica/eFacturaKonicaMinolta local/output conversie PDF', '.txt')
    
    # stergeFisiere('/home/efactura/efactura_konica/outputConversie', '.xml')
    # stergeFisiere('/home/efactura/efactura_konica/outputZipAPI', '.zip')
    # stergeFisiere('/home/efactura/efactura_konica/outputConversiePDF', '.pdf')
    # stergeFisiere('/home/efactura/efactura_konica/outputConversiePDF', '.txt')

    def lista_fisiere_xml(director_xml):
        fisiere_xml = []
        numarFactura=[]
        for nume_fisier in os.listdir(director_xml):
            if nume_fisier.endswith('.xml'):
                fisiere_xml.append(os.path.join(director_xml, nume_fisier))
                print('nume fisiere', nume_fisier)
                numarFactura.append((nume_fisier.split('_')[-1]).replace('.xml', ""))
        print("aici e numarul facturii cu split ca sa stim ",numarFactura)        
        print(len(fisiere_xml))
        return fisiere_xml
    

    def trimitereAnaf(fisiere_xml):
        listaIndexIncarcare.clear()  
        facturaIndex.clear()
        # apiDepunere = 'https://api.anaf.ro/test/FCTEL/rest/upload?standard=UBL&cif='+str(cif)

        for fisier_xml in fisiere_xml:
            try:
                with open(fisier_xml, 'r', encoding='utf-8') as file:
                    xml = file.read()
                    # print("ce e aici ", xml)

                if "<cbc:InvoiceTypeCode>389</cbc:InvoiceTypeCode>" in xml:
                    print("asta e AUTOFACTURA")
                    apiDepunere = f'https://api.anaf.ro/test/FCTEL/rest/upload?standard=UBL&cif={cif}&autofactura=DA'
                elif "CreditNote" in xml:
                    print('asta e credit note')
                    apiDepunere = 'https://api.anaf.ro/test/FCTEL/rest/upload?standard=CN&cif='+str(cif)
                else:
                    apiDepunere = 'https://api.anaf.ro/test/FCTEL/rest/upload?standard=UBL&cif='+str(cif)
                    
                response = requests.post(apiDepunere, headers=headers, data=xml)
                print('AICI AVEM RESPONSE',response)

                if response.status_code == 200:
                    resp = response.text
                    print("ASTA E RASPUNSUL ", resp)

                    root = ET.fromstring(resp)
                    index_incarcare = int(root.attrib['index_incarcare'])
                    listaIndexIncarcare.append(index_incarcare)

                    namespaces = {"cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"}
                    root = ET.fromstring(xml)
                    factura = root.find(".//cbc:ID", namespaces=namespaces).text
                    data = {'Factura': str(factura), 'Index': index_incarcare}
                    facturaIndex.append(data)
                    dictionarFacturi["mesaje"] = facturaIndex
                    
            except Exception as e:
                print("fisier cu probleme----------------->", fisier_xml)
                print("Eroare:", str(e))
                message = "fisier cu probleme----------------->" + str(fisier_xml)
                print("ASTA E RASPUNSUL LA EROARE ", response)
                listaMesajeEroare.append(message)
                with open('C:/Dezvoltare/E-Factura/2023/eFactura/Konica/eFacturaKonicaMinolta local/output conversie PDF/log.txt', 'a', encoding='utf-8') as log_file:
                # with open('/home/efactura/efactura_konica/outputConversiePDF/log.txt', 'a', encoding='utf-8') as log_file:
                    log_file.write("Eroare validare fisier: "+str(fisier_xml)+" \n")
                    log_file.write("Eroare la efectuarea cererii HTTP: "+str(response.status_code)+"\n")

    # Lista fișierelor XML se obține în afara funcției
    director_xml = "C:/Dezvoltare/E-Factura/2023/eFactura/Konica/eFacturaKonicaMinolta local/outs/"
    # director_xml = "/home/efactura/efactura_konica/outs"
    fisiere_xml = lista_fisiere_xml(director_xml)

    # Apelarea funcției trimitereAnaf cu lista de fișiere XML
    print('atatea mesaje de eroare sunt: ', len(listaMesajeEroare))
    numarFacturiErori = len(listaMesajeEroare)
    print("aici am trimis la anaf xml-uri")
    trimitereAnaf(fisiere_xml)

    # print("AICI E LISTA DE INDEX INCARCARE", listaIndexIncarcare)
    lungimeListaFacturi.append(len(listaIndexIncarcare))
    print(lungimeListaFacturi)
    # listaTest.append()
    
    
    stocareDictionarFacturi(dictionarFacturi)
    # print("asta e lista de facturi" ,listaFacturi(lungimeListaFacturi))
    
    
    print("import in baza de date cu succes!")
    time.sleep(5)

    
            
            # time.sleep(1)
    # --------------------------------STARE MESAj -----------------------------------
    
    def stareMesaj():
        listaIdDescarcare.clear()
        for i in range(0, len(listaIndexIncarcare)):
            apiStareMesaj = 'https://api.anaf.ro/test/FCTEL/rest/stareMesaj?id_incarcare='+str(listaIndexIncarcare[i])
            
            while True:  # buclă infinită
                stare = requests.get(apiStareMesaj, headers=headers, timeout=30)
                if stare.status_code == 200:
                    resp = stare.text
                    root = ET.fromstring(resp)
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
                print('id descarcare',id_descarcare, listaIndexIncarcare[i])   
            except:
                print(resp) 
    print("aici am facut starea mesajului")                 
    stareMesaj()
    print(listaIdDescarcare)

 

    # --------------------- DESCARCARE -------------------
    time.sleep(10)
    def descarcare():
        for i in range(0, len(listaIdDescarcare)):
            apiDescarcare = 'https://api.anaf.ro/test/FCTEL/rest/descarcare?id='+str(listaIdDescarcare[i])

            descarcare = requests.get(apiDescarcare, headers=headers, timeout=30)

            if descarcare.status_code == 200:
                # print("Cererea a fost efectuata cu succes!")
                with open('C:/Dezvoltare/E-Factura/2023/eFactura/Konica/eFacturaKonicaMinolta local/output zip api/fisier'+str(listaIdDescarcare[i])+'.zip', 'wb') as file:
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
        
    stocarePDF()
    print("aici stocam XML in BD")                  
    


    pdf_directory = 'C:/Dezvoltare/E-Factura/2023/eFactura/Konica/eFacturaKonicaMinolta local/output conversie PDF'
    # pdf_directory = '/home/efactura/efactura_konica/outputConversiePDF'
    # zip_file_path = '/home/efactura/efactura_konica/outputArhiveConversiePDF/rezultatArhiveConversie.zip'
    zip_file_path = 'C:/Dezvoltare/E-Factura/2023/eFactura/Konica/eFacturaKonicaMinolta local/output arhive conversie PDF/rezultatArhiveConversie.zip'
    make_archive(directory_path, os.path.join(pdf_directory, 'rezultat.zip'))   

    with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for pdf_file in os.listdir(pdf_directory):
            pdf_file_path = os.path.join(pdf_directory, pdf_file)
            zip_file.write(pdf_file_path, os.path.basename(pdf_file))
# eFactura()

