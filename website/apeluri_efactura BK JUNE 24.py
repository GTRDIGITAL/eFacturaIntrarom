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
    time.sleep(60)
        
    def mesajeanaf():
        
        time.sleep(15)
        cif = dateFirma['cui']
        headers = {'Authorization': dateFirma['header']}
        # val1 = 1699426800000  # 2023-11-08 09:00:00
        # X = 40
        # result = datetime.datetime.now() - datetime.timedelta(seconds=X)
        # val2 = int(datetime.datetime.timestamp(result)*1000)
        current_time = datetime.datetime.now()
        start_time = current_time - datetime.timedelta(days=60)
        val1 = int(time.mktime(start_time.timetuple())) * 1000

        # Restul codului rămâne neschimbat
        X = 0
        result = datetime.datetime.now() - datetime.timedelta(seconds=X)
        val2 = int(datetime.datetime.timestamp(result) * 1000)
        print("val1 ", val1)
        print("val2 ", val2)
        # apiListaFacturi = f'https://api.anaf.ro/test/FCTEL/rest/listaMesajePaginatieFactura?startTime={val1}&endTime={val2}&cif={cif}&pagina={6}'
        apiListaFacturi = f'https://api.anaf.ro/test/FCTEL/rest/listaMesajePaginatieFactura'
        
        params = {
        'startTime': val1,
        'endTime': val2,
        'cif': cif,
        'pagina': 1  
        }
        while True:
            try:
                response = requests.get(apiListaFacturi, params=params, headers=headers, timeout=30)

                if response.status_code == 200:
                    data = response.json()
                    print(data)
                    if 'eroare' in data:  # dacă starea nu mai este 'in prelucrare', se iese din buclă
                        # break
                        time.sleep(5)
                    else:  
                        numar_pagini = data.get('numar_total_pagini')
                        print(numar_pagini, 'numar pagini')
                        api_url_updated = f'{apiListaFacturi}?startTime={val1}&endTime={val2}&cif={cif}&pagina={numar_pagini}'
                        
                        listaMesaje = requests.get(api_url_updated, headers=headers, timeout=30)
                        raspunsMesajeFacturi = json.loads(listaMesaje.text)
                        # stocareMesajeAnaf(raspunsMesajeFacturi)
                        print('stocare a mesajelor cu success')
                        break 
                        # print("MESAJEEEEEEEEEEEE FACTURIIIIIIIIIIIIIIIIIIIII", raspunsMesajeFacturi)

            except:
                print(f'Eroare la cererea API, cod de stare: {response.status_code}')
                time.sleep(10)
        
    print('aici vedem mesajele anaf')
    # mesajeanaf()
    
            
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
    time.sleep(30)
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
    

    # def conversie():
    
    #     #--------------------------- CONVERSIE ------------------------------------
    #     # convert = 'https://webservicesp.anaf.ro/prod/FCTEL/rest/transformare/FACT1/DA'
    #     headerss={"Content-Type": "text/plain"}
    #     for filename in os.listdir(output_directory):
    #         if filename.endswith('.xml'):
    #             xml_file_path = os.path.join(output_directory, filename)
                
    #             # deschid fisierele de pe fisier si le trimit la anaf
    #             with open(xml_file_path, 'rb') as xml_file:
    #                 xml_data = xml_file.read()
                    
    #             if 'CreditNote' in str(xml_data):
    #                 convert = 'https://webservicesp.anaf.ro/prod/FCTEL/rest/transformare/FCN/DA'
    #             else:
    #                 convert = 'https://webservicesp.anaf.ro/prod/FCTEL/rest/transformare/FACT1/DA'
    #             response = requests.post(convert, data=xml_data, headers=headerss, timeout=30)
    #             filename=filename.replace(".xml","")

    #             if response.status_code == 200:
    #                 with open(f'C:/Dezvoltare/E-Factura/2023/eFactura/Konica/eFacturaKonicaMinolta local/output conversie PDF/{filename}.pdf', 'wb') as file:
    #                 # with open('/home/efactura/efactura_konica/outputConversiePDF/'+filename+'.pdf', 'wb') as file:
    #                     file.write(response.content)
    #                     print(f'Fisierul {filename} a fost convertit cu success')
    #             else:
    #                 print("Eroare la efectuarea cererii HTTP:", response.status_code)
    #                 print(response.text)
    
    # conversie() 
    # stocarePDF()
    # print('aici facem conversia si stocarea PDF in BD')


    # pdf_directory = 'C:/Dezvoltare/E-Factura/2023/eFactura/Konica/eFacturaKonicaMinolta local/output conversie PDF'
    # # pdf_directory = '/home/efactura/efactura_konica/outputConversiePDF'
    # # zip_file_path = '/home/efactura/efactura_konica/outputArhiveConversiePDF/rezultat'+str(current_datetime)+'.zip'
    # # zip_file_path = '/home/efactura/efactura_konica/outputArhiveConversiePDF/rezultatArhiveConversie.zip'
    # zip_file_path = 'C:/Dezvoltare/E-Factura/2023/eFactura/Konica/eFacturaKonicaMinolta local/output arhive conversie PDF/rezultatArhiveConversie.zip'
    # make_archive(directory_path, os.path.join(pdf_directory, 'rezultat.zip'))   

    # with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
    #     for pdf_file in os.listdir(pdf_directory):
    #         pdf_file_path = os.path.join(pdf_directory, pdf_file)
    #         zip_file.write(pdf_file_path, os.path.basename(pdf_file))
    
    def conversie():
        # output_directory = 'C:/Dezvoltare/E-Factura/2023/eFactura/Konica/eFacturaKonicaMinolta local/output conversie'
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
                        with open(f'C:/Dezvoltare/E-Factura/2023/eFactura/Konica/eFacturaKonicaMinolta local/output conversie PDF/{filename_no_extension}.pdf', 'wb') as file:
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

    
    # conversie()
    
    print('aici facem conversia in PDF')


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
