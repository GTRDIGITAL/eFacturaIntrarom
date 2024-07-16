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

    # stergeFisiere('C:/Dezvoltare/E-Factura/2023/eFactura/Intrarom/Intrarom local - Copy/output conversie', '.xml')
    # stergeFisiere('C:/Dezvoltare/E-Factura/2023/eFactura/Intrarom/Intrarom local - Copy/output zip api', '.zip')
    # stergeFisiere('C:/Dezvoltare/E-Factura/2023/eFactura/Intrarom/Intrarom local - Copy/output conversie PDF', '.pdf')
    # stergeFisiere('C:/Dezvoltare/E-Factura/2023/eFactura/Intrarom/Intrarom local - Copy/output conversie PDF', '.txt')
    # stergeFisiere('C:/Dezvoltare/E-Factura/2023/eFactura/Intrarom/Intrarom local - Copy/Baza de date vanzari', '.txt')
    # stergeFisiere('C:/Dezvoltare/E-Factura/2023/eFactura/Intrarom/Intrarom local - Copy/outs', '.xml')
    
    stergeFisiere('/home/efactura/efactura_intrarom/outputConversie', '.xml')
    stergeFisiere('/home/efactura/efactura_intrarom/outputZipAPI', '.zip')
    stergeFisiere('/home/efactura/efactura_intrarom/outputConversiePDF', '.pdf')
    stergeFisiere('/home/efactura/efactura_intrarom/outputConversiePDF', '.txt')
    stergeFisiere('/home/efactura/efactura_intrarom/bazaDateVanzari', '.txt')

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
                # with open('C:/Dezvoltare/E-Factura/2023/eFactura/Intrarom/Intrarom local - Copy/output conversie PDF/log.txt', 'a', encoding='utf-8') as log_file:
                with open('/home/efactura/efactura_intrarom/outputConversiePDF/log.txt', 'a', encoding='utf-8') as log_file:
                    log_file.write("Eroare validare fisier: "+str(fisier_xml)+" \n")
                    log_file.write("Eroare la efectuarea cererii HTTP: "+str(response.status_code)+"\n")
        
    # Lista fișierelor XML se obține în afara funcției
    # director_xml = "C:/Dezvoltare/E-Factura/2023/eFactura/Intrarom/Intrarom local - Copy/outs/"
    director_xml = "/home/efactura/efactura_intrarom/outs"
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
    
    for item in dictionarFacturi["mesaje"]:
        factura = item["Factura"]
        index_solicitare = item["Index"]
        # with open('C:/Dezvoltare/E-Factura/2023/eFactura/Intrarom/Intrarom local - Copy/Baza de date vanzari/facturiTransmise.txt', 'a', encoding='utf-8') as raspunsANAFIndex:
        with open('/home/efactura/efactura_intrarom/bazaDateVanzari/facturiTransmise.txt', 'a', encoding='utf-8') as raspunsANAFIndex:
            raspunsANAFIndex.write("Factura: "+str(factura)+" "+ "Index: " +str(index_solicitare)+" \n")
    
    stocareDictionarFacturi(dictionarFacturi)
    
    # print("asta e lista de facturi" ,listaFacturi(lungimeListaFacturi))
    

    print("import in baza de date cu succes!")
