import xml.etree.ElementTree as ET
from openpyxl import Workbook
import os
import pandas as pd
from sqlalchemy import create_engine
import json
import math
import io
import unicodedata

def normal_round(n, decimals=0):
    expoN = n * 10 ** decimals
    if abs(expoN) - abs(math.floor(expoN)) < 0.5:
        return math.floor(expoN) / 10 ** decimals
    return math.ceil(expoN) / 10 ** decimals


def extract_data_from_element(element):
    data = {}
    for child in element:
        if list(child):
            data.update(extract_data_from_element(child))
        else:
            data[child.tag] = child.text
    return data

def citeste_configurare(file_path):
    with open(file_path, 'r') as file:
        config = json.load(file)
    return config

config = citeste_configurare('config.json')
mysql_config = config['mysql']

def xml_to_excel(xml_file, excel_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    wb = Workbook()

    for tag in ['SalesCrMemoHeader', 'SelfBillingInvoiceHeader', 'SalesInvoiceHeader']:
        ws = wb.create_sheet(title=tag)

        headers = set()
        for element in root.findall('.//' + tag):
            headers.update(element.attrib.keys())
            for child in element.iter():
                headers.add(child.tag)
        ws.append(list(headers))

        for element in root.findall('.//' + tag):
            row_data = []
            for header in headers:
                if header in element.attrib:
                    row_data.append(element.attrib[header])
                else:
                    child = element.find('.//' + header)
                    if child is not None:
                        row_data.append(child.text)
                    else:
                        row_data.append(None)
            ws.append(row_data)

    default_sheet = wb['Sheet']
    wb.remove(default_sheet)

    wb.save(excel_file)

xml_file = "C:/Dezvoltare/E-Factura/2023/eFactura/Konica/Romania GT E-Invoicing 010124 to 260324.xml"
# excel_file = 'output.xlsx'
# excel_file = "C:/Dezvoltare/E-Factura/2023/eFactura/Konica/output.xlsx"
excel_file = pd.ExcelFile('C:/Dezvoltare/E-Factura/2023/eFactura/Konica/output.xlsx')
# xml_to_excel(xml_file, excel_file)

def stergeFisiere(directory_path, file_extension):
    try:
        for filename in os.listdir(directory_path):
            file_path = os.path.join(directory_path, filename)
            if filename.endswith(file_extension):
                os.remove(file_path)
                print(f"Fisierul {filename} a fost sters.")
    except Exception as e:
        print(f"Eroare la stergerea fișierelor: {str(e)}")

stergeFisiere('C:/Dezvoltare/E-Factura/2023/eFactura/Konica/eFacturaKonicaMinolta/outs', '.xml')

strada = "Str. C.A Rosetti 17, Etj 1, Birou 105, Campus 02"
oras = "SECTOR2"
# codPostal = "000000"
countrySubentity = "RO-B"
country = "RO"
vatID ="RO30770893" 
numeCompanie = "Konica Minolta Marketing Services Limited (RO)"


engine = create_engine(f"mysql://{config['mysql']['user']}:{config['mysql']['password']}@{config['mysql']['host']}/{config['mysql']['database']}")
print("CONECTAT LA BAZA")
query = "SELECT * FROM clients WHERE region IS NOT NULL"

bazaClienti = pd.read_sql(query, engine)

engine.dispose()
print("Deconectat de la baza de date")

dictClientName=bazaClienti.set_index('regno').to_dict()['Name']
dictClientCountry=bazaClienti.set_index('regno').to_dict()['Country']
dictClientCity=bazaClienti.set_index('regno').to_dict()['City']
# dictClientRegNo=bazaClienti.set_index('regno').to_dict()['regno']
dictClientStreet=bazaClienti.set_index('regno').to_dict()['Street']
dictClientRegiune=bazaClienti.set_index('regno').to_dict()['region']
dictTaxCodeVzIDTVA={'RO-STDVAT-19':"S", 'RO-EXEMPT-0':'AE'}


output = pd.read_excel(excel_file)
if "SalesInvoiceHeader" in excel_file.sheet_names:
    
    Sales_EFACTURA = pd.read_excel(excel_file, sheet_name='SalesInvoiceHeader')
    Sales_EFACTURA=Sales_EFACTURA.loc[Sales_EFACTURA["SI_BillToCountryCode"]=="RO"]

    listaNumarFact = list(set(list(Sales_EFACTURA["SI_DocNo"])))
    

    Sales_EFACTURA["SI_UnitPrice"] = Sales_EFACTURA["SI_UnitPrice"].astype(str).str.replace(',', '').astype(float)
    Sales_EFACTURA["Pret Unitar"] = Sales_EFACTURA['SI_UnitPrice']

    Sales_EFACTURA["SI_Amount"] = Sales_EFACTURA["SI_Amount"].astype(str).str.replace(',', '').astype(float)
    Sales_EFACTURA["SI_AmountInclVAT"] = Sales_EFACTURA["SI_AmountInclVAT"].astype(str).str.replace(',', '').astype(float)
    Sales_EFACTURA["SI_VATPerc"] = Sales_EFACTURA["SI_VATPerc"].astype(str).str.replace(',', '').astype(float)
    Sales_EFACTURA["Valoare linia TVA"] = Sales_EFACTURA["SI_Amount"] * (Sales_EFACTURA["SI_VATPerc"] / 100)
    Sales_EFACTURA["CodRegiune"]=Sales_EFACTURA["SI_VATRegNo"].map(dictClientRegiune)
    Sales_EFACTURA["Name"]=Sales_EFACTURA["SI_VATRegNo"].map(dictClientName)
    Sales_EFACTURA["City"]=Sales_EFACTURA["SI_VATRegNo"].map(dictClientCity)
    Sales_EFACTURA["Country"]=Sales_EFACTURA["SI_VATRegNo"].map(dictClientCountry)
    Sales_EFACTURA["Street"]=Sales_EFACTURA["SI_VATRegNo"].map(dictClientStreet)
    
    print(Sales_EFACTURA["Valoare linia TVA"])
    
    
    # Sales_EFACTURA["Valoare linia TVA"] = Sales_EFACTURA["SI_Amount"] * (Sales_EFACTURA["SI_VATPerc"] / 100)
    Sales_EFACTURA["Valoare linie cu TVA"] = Sales_EFACTURA["SI_AmountInclVAT"]
    Sales_EFACTURA["ID TVA"] = Sales_EFACTURA["SI_VATIdentifier"].map(dictTaxCodeVzIDTVA)
    Sales_EFACTURA["Cod Unitate Masura"]="H87" #DE SCHIMBAAAAAAAAAAAAAAAAAAAT CAND PRIMIM
    Sales_EFACTURA.loc[Sales_EFACTURA["SI_CurrencyCode"]=="RON", "SI_Amount_Valuta"]=0
    Sales_EFACTURA.loc[Sales_EFACTURA["SI_CurrencyCode"]!="RON", "SI_Amount_Valuta"]=Sales_EFACTURA["SI_Amount"].astype(float)
    Sales_EFACTURA["Valoare linia TVA (Valuta)"]=Sales_EFACTURA["SI_Amount_Valuta"].fillna(0)*(Sales_EFACTURA["SI_VATPerc"].fillna(0)/100)
    Sales_EFACTURA.to_excel("C:/Dezvoltare/E-Factura/2023/eFactura/Konica/eFacturaKonicaMinolta/Baza de date vanzari/Sales.xlsx")
    Sales_EFACTURA["Valoare linie cu TVA (Valuta)"]=Sales_EFACTURA["SI_AmountInclVAT"].fillna(0)*(Sales_EFACTURA["SI_VATPerc"].fillna(0)/100)


    # print(listaNumarFact)
    Sales_EFACTURA["SI_Amount"] = Sales_EFACTURA["SI_Amount"].astype(str).str.replace(',', '').astype(float)
    # Sales_EFACTURA.to_excel("C:/Dezvoltare/E-Factura/2023/eFactura/Konica/eFacturaKonicaMinolta/Baza de date vanzari/Sales.xlsx")
    totalFactura=Sales_EFACTURA["SI_Amount"].sum()
    print(totalFactura)
    primaFactura = list(Sales_EFACTURA["SI_DocNo"])[0]
    ultimaFactura=list(Sales_EFACTURA["SI_DocNo"])[-1]
    # print(totalFactura, primaFactura, ultimaFactura)
    print("asta e prima factura in prelucrare_date.py ",primaFactura)

    issue_date = pd.to_datetime(Sales_EFACTURA["SI_DocumentDate"], format='%d/%m/%Y').dt.strftime('%Y-%m-%d').iloc[0]
    nrFacturiTrimise = len(listaNumarFact)

if "SalesCrMemoHeader" in excel_file.sheet_names:
    CreditMemo_EFACTURA = pd.read_excel(excel_file, sheet_name='SalesCrMemoHeader')
    listaNumarFactCM = list(set(list(CreditMemo_EFACTURA["SC_DocNo"])))
    CreditMemo_EFACTURA=CreditMemo_EFACTURA.loc[CreditMemo_EFACTURA["SC_BillToCountryCode"]=="RO"]
    CreditMemo_EFACTURA["SC_Amount"] = CreditMemo_EFACTURA["SC_Amount"].astype(str).str.replace(',', '').astype(float)
    CreditMemo_EFACTURA["SC_AmountInclVAT"] = CreditMemo_EFACTURA["SC_AmountInclVAT"].astype(str).str.replace(',', '').astype(float)
    CreditMemo_EFACTURA["SC_VATPerc"] = CreditMemo_EFACTURA["SC_VATPerc"].astype(str).str.replace(',', '').astype(float)
    CreditMemo_EFACTURA["SC_UnitPrice"] = CreditMemo_EFACTURA["SC_UnitPrice"].astype(str).str.replace(',', '').astype(float)
    CreditMemo_EFACTURA["Pret Unitar"] = CreditMemo_EFACTURA['SC_UnitPrice']
    CreditMemo_EFACTURA["Valoare linia TVA"] = CreditMemo_EFACTURA["SC_Amount"] * (CreditMemo_EFACTURA["SC_VATPerc"] / 100)
    CreditMemo_EFACTURA["Valoare linie cu TVA"] = CreditMemo_EFACTURA["SC_AmountInclVAT"]
    
    CreditMemo_EFACTURA["Cod Unitate Masura"]="H87" #DE SCHIMBAAAAAAAAAAAAAAAAAAAT CAND PRIMIM
    CreditMemo_EFACTURA.loc[CreditMemo_EFACTURA["SC_CurrencyCode"]=="RON", "SC_Amount_Valuta"]=0
    CreditMemo_EFACTURA.loc[CreditMemo_EFACTURA["SC_CurrencyCode"]!="RON", "SC_Amount_Valuta"]=CreditMemo_EFACTURA["SC_Amount"]
    CreditMemo_EFACTURA["Valoare linia TVA (Valuta)"]=CreditMemo_EFACTURA["SC_Amount_Valuta"]*(CreditMemo_EFACTURA["SC_VATPerc"]/100)
    CreditMemo_EFACTURA["Valoare linie cu TVA (Valuta)"]=CreditMemo_EFACTURA["SC_AmountInclVAT"]*(CreditMemo_EFACTURA["SC_VATPerc"]/100)
    CreditMemo_EFACTURA.loc[CreditMemo_EFACTURA["SC_VATPerc"].astype(str)=="0.0", "SC_VATIdentifier"]="RO-EXEMPT-0"
    CreditMemo_EFACTURA.loc[CreditMemo_EFACTURA["SC_VATPerc"].astype(str)=="19.0", "SC_VATIdentifier"]="RO-STDVAT-19"
    print(CreditMemo_EFACTURA["SC_VATPerc"])
    CreditMemo_EFACTURA["ID TVA"] = CreditMemo_EFACTURA["SC_VATIdentifier"].map(dictTaxCodeVzIDTVA)
    CreditMemo_EFACTURA["CodRegiune"]=CreditMemo_EFACTURA["SC_VATRegNo"].map(dictClientRegiune)
    CreditMemo_EFACTURA["Name"]=CreditMemo_EFACTURA["SC_VATRegNo"].map(dictClientName)
    CreditMemo_EFACTURA["City"]=CreditMemo_EFACTURA["SC_VATRegNo"].map(dictClientCity)
    CreditMemo_EFACTURA["Country"]=CreditMemo_EFACTURA["SC_VATRegNo"].map(dictClientCountry)
    CreditMemo_EFACTURA["Street"]=CreditMemo_EFACTURA["SC_VATRegNo"].map(dictClientStreet)
    CreditMemo_EFACTURA.to_excel("C:/Dezvoltare/E-Factura/2023/eFactura/Konica/eFacturaKonicaMinolta/Baza de date vanzari/Credit Notes.xlsx")
    
    
# print(issue_date)
if 'SalesInvoiceHeader' in excel_file.sheet_names:
    for i in range(0, len(listaNumarFact)):
        df_fact_curenta = Sales_EFACTURA.groupby(["SI_DocNo"]).get_group(listaNumarFact[i])
        issue_date = pd.to_datetime(df_fact_curenta["SI_DocumentDate"], format='%d/%m/%Y').dt.strftime('%Y-%m-%d').iloc[0]
        data_scadenta=pd.to_datetime(df_fact_curenta["SI_DueDate"], format='%d/%m/%Y').dt.strftime('%Y-%m-%d').iloc[0]
        if df_fact_curenta["SI_BillToCountryCode"].iloc[0]=="RO":
            subtotalTva = df_fact_curenta.groupby("SI_VATPerc")["Valoare linia TVA"].sum().reset_index()
            subtotalBaza=df_fact_curenta.groupby("SI_VATPerc")["SI_Amount"].sum().reset_index()
            subtotalIDTVA=df_fact_curenta.groupby("ID TVA")["SI_VATPerc"].sum().reset_index()
            
            if str(df_fact_curenta["SI_CurrencyCode"].iloc[0])=="RON":
                total_amount = 0

                XML_Header = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n
                <Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2" xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"\n xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2" xmlns:ns4="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"\n xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2 http://docs.oasis-open.org/ubl/os-UBL-2.1/xsd/maindoc/UBL-Invoice-2.1.xsd">
                <cbc:CustomizationID>urn:cen.eu:en16931:2017#compliant#urn:efactura.mfinante.ro:CIUS-RO:1.0.1</cbc:CustomizationID>
                <cbc:ID>{str(df_fact_curenta["SI_DocNo"].iloc[0]).replace(".0", "")}</cbc:ID>
                <cbc:IssueDate>{issue_date}</cbc:IssueDate>
                <cbc:DueDate>{data_scadenta}</cbc:DueDate>
                <cbc:InvoiceTypeCode>380</cbc:InvoiceTypeCode>
                <cbc:Note>Sell-to-Contact:{str(df_fact_curenta["SI_SellToContact"].iloc[0])}</cbc:Note>
                <cbc:Note>Your Ref. No:{str(df_fact_curenta["SI_ExternalDocNo"].iloc[0])}</cbc:Note>
                <cbc:Note>Salesperson Code:{str(df_fact_curenta["SI_SalespersonCode"].iloc[0])}</cbc:Note>
                <cbc:Note>{df_fact_curenta["SI_RemittanceDetails"].iloc[0]}</cbc:Note>
                <cbc:Note>Project No.: {df_fact_curenta["SI_ProjectNo"].iloc[0]}</cbc:Note>
                
                <cbc:DocumentCurrencyCode>RON</cbc:DocumentCurrencyCode>
                '''

                AccountingSupplierParty = '''
                <cac:AccountingSupplierParty>
                    <cac:Party>
                        <cac:PostalAddress>
                            <cbc:StreetName>'''+str(strada)+'''</cbc:StreetName>
                            <cbc:CityName>'''+str(oras)+'''</cbc:CityName>
                            <cbc:CountrySubentity>'''+str(countrySubentity)+'''</cbc:CountrySubentity>
                            <cac:Country>
                                <cbc:IdentificationCode>'''+str(country)+'''</cbc:IdentificationCode>
                            </cac:Country>
                        </cac:PostalAddress>
                        <cac:PartyTaxScheme>
                            <cbc:CompanyID>'''+str(vatID)+'''</cbc:CompanyID>
                            <cac:TaxScheme>
                                <cbc:ID>VAT</cbc:ID>
                            </cac:TaxScheme>
                        </cac:PartyTaxScheme>
                        <cac:PartyLegalEntity>
                            <cbc:RegistrationName>'''+str(numeCompanie)+'''</cbc:RegistrationName>
                            <cbc:CompanyID>'''+str(vatID)+'''</cbc:CompanyID>
                        </cac:PartyLegalEntity>
                    </cac:Party>
                </cac:AccountingSupplierParty>
                '''
                
                
                if str(df_fact_curenta["SI_BillToAddress"].iloc[0]) == "  ":
                    AccountingCustomerPartyXML=f'''
                    <cac:AccountingCustomerParty>
                        <cac:Party>
                            <cac:PostalAddress>
                                <cbc:StreetName>{str(df_fact_curenta["City"].iloc[0])}</cbc:StreetName>
                                <cbc:CityName>{str(df_fact_curenta["City"].iloc[0])}</cbc:CityName>
                                <cbc:CountrySubentity>RO-{df_fact_curenta["CodRegiune"].iloc[0]}</cbc:CountrySubentity>
                                <cac:Country>
                                    <cbc:IdentificationCode>{str(df_fact_curenta["Country"].iloc[0])}</cbc:IdentificationCode>
                                </cac:Country>
                            </cac:PostalAddress>
                            <cac:PartyTaxScheme>
                                <cbc:CompanyID>{str(df_fact_curenta["SI_VATRegNo"].iloc[0])}</cbc:CompanyID>
                                <cac:TaxScheme>
                                    <cbc:ID>VAT</cbc:ID>
                                </cac:TaxScheme>
                            </cac:PartyTaxScheme>
                            <cac:PartyLegalEntity>
                                <cbc:RegistrationName>{str(df_fact_curenta["Name"].iloc[0])}</cbc:RegistrationName>
                                <cbc:CompanyID>{str(df_fact_curenta[""].iloc[0])}</cbc:CompanyID>
                            </cac:PartyLegalEntity>
                        </cac:Party>
                    </cac:AccountingCustomerParty>'''
                else:
                    AccountingCustomerPartyXML=f'''
                <cac:AccountingCustomerParty>
                    <cac:Party>
                        <cac:PostalAddress>
                            <cbc:StreetName>{str(df_fact_curenta["Street"].iloc[0])}</cbc:StreetName>
                            <cbc:CityName>{str(df_fact_curenta["City"].iloc[0])}</cbc:CityName> 
                            <cbc:CountrySubentity>RO-{df_fact_curenta["CodRegiune"].iloc[0]}</cbc:CountrySubentity>
                            <cac:Country>
                                <cbc:IdentificationCode>{str(df_fact_curenta["Country"].iloc[0])}</cbc:IdentificationCode>
                            </cac:Country>
                        </cac:PostalAddress>
                        <cac:PartyTaxScheme>
                            <cbc:CompanyID>{str(df_fact_curenta["SI_VATRegNo"].iloc[0])}</cbc:CompanyID>
                            <cac:TaxScheme>
                                <cbc:ID>VAT</cbc:ID>
                            </cac:TaxScheme>
                        </cac:PartyTaxScheme>
                        <cac:PartyLegalEntity>
                            <cbc:RegistrationName>{str(df_fact_curenta["Name"].iloc[0])}</cbc:RegistrationName>
                            <cbc:CompanyID>{str(df_fact_curenta["SI_VATRegNo"].iloc[0])}</cbc:CompanyID>
                        </cac:PartyLegalEntity>
                    </cac:Party>
                </cac:AccountingCustomerParty>'''
                invoiceLine = ""
                line_count = 1
                total_tva=0
                # print(subtotalTva)
                # <cbc:ID>{row["ID TVA"]}</cbc:ID>
                for index, row in subtotalTva.iterrows():
                    taxamount=subtotalTva["Valoare linia TVA"].sum()
                    baza = subtotalBaza["SI_Amount"].sum()
                    taxamount = normal_round(taxamount, decimals=2)
                    taxamount2 = row["Valoare linia TVA"]
                    taxamount2 = normal_round(taxamount2, decimals=2)
                    if subtotalIDTVA["ID TVA"][index]=="S":
                        TaxTotal = f'''
                        <cac:TaxTotal>
                            <cbc:TaxAmount currencyID="RON">{(str(taxamount))}</cbc:TaxAmount>
                            <cac:TaxSubtotal>
                                <cbc:TaxableAmount currencyID="RON">{str(round(float(str(baza)),2))}</cbc:TaxableAmount>
                                <cbc:TaxAmount currencyID="RON">{(str(taxamount2))}</cbc:TaxAmount>
                                <cac:TaxCategory>
                                    
                                    <cbc:ID>{subtotalIDTVA["ID TVA"][index]}</cbc:ID>
                                    <cbc:Percent>{str(round(float(str(row["SI_VATPerc"])),2))}</cbc:Percent>
                                    <cac:TaxScheme>
                                        <cbc:ID>VAT</cbc:ID>
                                    </cac:TaxScheme>
                                </cac:TaxCategory>
                            </cac:TaxSubtotal>
                        </cac:TaxTotal>\n'''
                    else:
                        TaxExemptionReasonCode="VATEX-EU-AE"
                        TaxTotal = f'''
                        <cac:TaxTotal>
                            <cbc:TaxAmount currencyID="RON">{(str(taxamount))}</cbc:TaxAmount>
                            <cac:TaxSubtotal>
                                <cbc:TaxableAmount currencyID="RON">{str(round(float(str(baza)),2))}</cbc:TaxableAmount>
                                <cbc:TaxAmount currencyID="RON">{(str(taxamount2))}</cbc:TaxAmount>
                                <cac:TaxCategory>
                                    
                                    <cbc:ID>{subtotalIDTVA["ID TVA"][index]}</cbc:ID>

                                    <cbc:Percent>{str(round(float(str(row["SI_VATPerc"])),2))}</cbc:Percent>
                                    <cbc:TaxExemptionReasonCode>{TaxExemptionReasonCode}</cbc:TaxExemptionReasonCode>
                                    <cac:TaxScheme>
                                        <cbc:ID>VAT</cbc:ID>
                                    </cac:TaxScheme>
                                </cac:TaxCategory>
                            </cac:TaxSubtotal>
                        </cac:TaxTotal>\n'''
                        

                
                for index, row in df_fact_curenta.iterrows():
                    line_amount = row["SI_Amount"]
                    val_cu_tva = row["Valoare linie cu TVA"]
                    
                    total_tva += val_cu_tva
                    total_amount += line_amount
                    invoiceLine += f'''<cac:InvoiceLine>
                            <cbc:ID>{line_count}</cbc:ID>
                            <cbc:InvoicedQuantity unitCode="{row["Cod Unitate Masura"]}">{row["SI_Quantity"]}</cbc:InvoicedQuantity>
                            <cbc:LineExtensionAmount currencyID="RON">{str(round(float(str(row["SI_Amount"])),2))}</cbc:LineExtensionAmount>
                            <cac:Item>
                                <cbc:Name>{row["SI_Description"]}</cbc:Name>
                                <cac:ClassifiedTaxCategory>
                                    <cbc:ID>{row["ID TVA"]}</cbc:ID>
                                    <cbc:Percent>{str(round(float(str(row["SI_VATPerc"])),2))}</cbc:Percent>
                                    <cac:TaxScheme>
                                        <cbc:ID>VAT</cbc:ID>
                                    </cac:TaxScheme>
                                </cac:ClassifiedTaxCategory>
                            </cac:Item>
                            <cac:Price>
                                <cbc:PriceAmount currencyID="RON">{str(round(float(str(row["Pret Unitar"])),2))}</cbc:PriceAmount>
                            </cac:Price>
                        </cac:InvoiceLine>'''
                        
                    
                    
                    # Incrementați numărul elementului pentru următoarea linie din factură
                    line_count += 1
                # total_amount_with_vat = total_amount * (1 + row["Cota"] / 100)
                total_amount_with_vat=normal_round(total_amount, decimals=2)+normal_round(taxamount2, decimals=2)
                # total_amount_with_vat=normal_round(total_amount_with_vat,)
                # print(row["Inv. No"], total_tva)
                # print(str(df_fact_curenta["Inv. No"].iloc[0]).replace(".0", "") ,total_amount_without_vat)
                
                PaymentMeans = f'''
                <cac:PaymentMeans>
                    <cbc:PaymentMeansCode>10</cbc:PaymentMeansCode>
                    <cac:PayeeFinancialAccount>
                        <cbc:ID>{df_fact_curenta["SI_BankAccNo"].iloc[0]}</cbc:ID>
                        <cbc:Name>{df_fact_curenta["SI_BankName"].iloc[0]}</cbc:Name>
                        <cac:FinancialInstitutionBranch>
                            <cbc:ID>{df_fact_curenta["SI_BankSwiftCode"].iloc[0]}</cbc:ID>
                        </cac:FinancialInstitutionBranch>
                    </cac:PayeeFinancialAccount>
                </cac:PaymentMeans>'''

                
                LegalMonetary = f'''
                <cac:LegalMonetaryTotal>
                    <cbc:LineExtensionAmount currencyID="RON">{str(round(float(str(total_amount)),2))}</cbc:LineExtensionAmount>
                    <cbc:TaxExclusiveAmount currencyID="RON">{str(round(float(str(total_amount)),2))}</cbc:TaxExclusiveAmount>
                    <cbc:TaxInclusiveAmount currencyID="RON">{str(round(float(str(total_amount_with_vat)),2))}</cbc:TaxInclusiveAmount>
                    <cbc:AllowanceTotalAmount currencyID="RON">0.00</cbc:AllowanceTotalAmount>
                    <cbc:ChargeTotalAmount currencyID="RON">0.00</cbc:ChargeTotalAmount>
                    <cbc:PrepaidAmount currencyID="RON">0.00</cbc:PrepaidAmount>
                    <cbc:PayableRoundingAmount currencyID="RON">0.00</cbc:PayableRoundingAmount>
                    <cbc:PayableAmount currencyID="RON">{str(round(float(str(total_amount_with_vat)),2))}</cbc:PayableAmount>
                </cac:LegalMonetaryTotal>'''
                
                eFacturaXML = XML_Header + AccountingSupplierParty + AccountingCustomerPartyXML + PaymentMeans + TaxTotal + LegalMonetary + invoiceLine +"\n</Invoice>"
                def remove_diacritics(input_str):
                    nfkd_form = unicodedata.normalize('NFKD', input_str)
                    return ''.join([c for c in nfkd_form if not unicodedata.combining(c)])

                eFacturaXML = remove_diacritics(eFacturaXML)
                eFacturaXML=eFacturaXML.replace("&"," ")

                # Scrie conținutul în fișierul XML
                with io.open(f"C:/Dezvoltare/E-Factura/2023/eFactura/Konica/eFacturaKonicaMinolta/outs/SalesInvoice_{str(listaNumarFact[i]).replace('.0', '')}.xml", "w", encoding="utf-8") as f:
                    f.write(eFacturaXML)
        #===================invoice in valuta==================================================
        
        else:
            currency=str(df_fact_curenta["SI_CurrencyCode"].iloc[0])
                
            listaCote = list(set(list(df_fact_curenta["SI_VATPerc"])))
            subtotalTvaLEI=df_fact_curenta.groupby("SI_VATPerc")["Valoare linia TVA"].sum().reset_index()
            subtotalTva = df_fact_curenta.groupby("SI_VATPerc")["Valoare linia TVA (Valuta)"].sum().reset_index()
            subtotalBaza=df_fact_curenta.groupby("SI_VATPerc")["SI_Amount"].sum().reset_index()
            subtotalBazaValuta=df_fact_curenta.groupby("SI_VATPerc")["SI_Amount_Valuta"].sum().reset_index()
            subtotalTvaValuta=df_fact_curenta.groupby("SI_VATPerc")["Valoare linia TVA (Valuta)"].sum().reset_index()
            subtotalIDTVA=df_fact_curenta.groupby("ID TVA")["SI_VATPerc"].sum().reset_index()
            
            total_amount = 0
            tva_total=0
            #{str(df_fact_curenta["Journal"].iloc[0]).replace(".0", "")}
            
            XML_Header = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n
            <Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2" xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"\n xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2" xmlns:ns4="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"\n xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2 http://docs.oasis-open.org/ubl/os-UBL-2.1/xsd/maindoc/UBL-Invoice-2.1.xsd">
            <cbc:CustomizationID>urn:cen.eu:en16931:2017#compliant#urn:efactura.mfinante.ro:CIUS-RO:1.0.1</cbc:CustomizationID>
            <cbc:ID>{str(df_fact_curenta["SI_DocNo"].iloc[0]).replace(".0", "")}</cbc:ID>
            <cbc:IssueDate>{issue_date}</cbc:IssueDate>
            <cbc:DueDate>{data_scadenta}</cbc:DueDate>
            <cbc:InvoiceTypeCode>380</cbc:InvoiceTypeCode>
            <cbc:Note>Sell-to-Contact:{str(df_fact_curenta["SI_SellToContact"].iloc[0])}</cbc:Note>
            <cbc:Note>Your Ref. No:{str(df_fact_curenta["SI_ExternalDocNo"].iloc[0])}</cbc:Note>
            <cbc:Note>Salesperson Code:{str(df_fact_curenta["SI_SalespersonCode"].iloc[0])}</cbc:Note>
            <cbc:Note>{df_fact_curenta["SI_RemittanceDetails"].iloc[0]}</cbc:Note>
            <cbc:Note>Project No.: {df_fact_curenta["SI_ProjectNo"].iloc[0]}</cbc:Note>
           
            <cbc:DocumentCurrencyCode>{str(df_fact_curenta['SI_CurrencyCode'].iloc[0])}</cbc:DocumentCurrencyCode>
            <cbc:TaxCurrencyCode>RON</cbc:TaxCurrencyCode>
            '''

            AccountingSupplierParty = '''
            <cac:AccountingSupplierParty>
                <cac:Party>
                    <cac:PostalAddress>
                        <cbc:StreetName>'''+str(strada)+'''</cbc:StreetName>
                        <cbc:CityName>'''+str(oras)+'''</cbc:CityName>
                        <cbc:CountrySubentity>'''+str(countrySubentity)+'''</cbc:CountrySubentity>
                        <cac:Country>
                            <cbc:IdentificationCode>'''+str(country)+'''</cbc:IdentificationCode>
                        </cac:Country>
                    </cac:PostalAddress>
                    <cac:PartyTaxScheme>
                        <cbc:CompanyID>'''+str(vatID)+'''</cbc:CompanyID>
                        <cac:TaxScheme>
                            <cbc:ID>VAT</cbc:ID>
                        </cac:TaxScheme>
                    </cac:PartyTaxScheme>
                    <cac:PartyLegalEntity>
                        <cbc:RegistrationName>'''+str(numeCompanie)+'''</cbc:RegistrationName>
                        <cbc:CompanyID>'''+str(vatID)+'''</cbc:CompanyID>
                    </cac:PartyLegalEntity>
                </cac:Party>
            </cac:AccountingSupplierParty>
            '''
            
            if str(df_fact_curenta["SI_BillToAddress"].iloc[0]) == "  ":
                AccountingCustomerPartyXML=f'''
                    <cac:AccountingCustomerParty>
                        <cac:Party>
                            <cac:PostalAddress>
                                <cbc:StreetName>{str(df_fact_curenta["City"].iloc[0])}</cbc:StreetName>
                                <cbc:CityName>{str(df_fact_curenta["City"].iloc[0])}</cbc:CityName>
                                <cbc:CountrySubentity>RO-{df_fact_curenta["CodRegiune"].iloc[0]}</cbc:CountrySubentity>
                                <cac:Country>
                                    <cbc:IdentificationCode>{str(df_fact_curenta["Country"].iloc[0])}</cbc:IdentificationCode>
                                </cac:Country>
                            </cac:PostalAddress>
                            <cac:PartyTaxScheme>
                                <cbc:CompanyID>{str(df_fact_curenta["SI_VATRegNo"].iloc[0])}</cbc:CompanyID>
                                <cac:TaxScheme>
                                    <cbc:ID>VAT</cbc:ID>
                                </cac:TaxScheme>
                            </cac:PartyTaxScheme>
                            <cac:PartyLegalEntity>
                                <cbc:RegistrationName>{str(df_fact_curenta["Name"].iloc[0])}</cbc:RegistrationName>
                                <cbc:CompanyID>{str(df_fact_curenta["SI_VATRegNo"].iloc[0])}</cbc:CompanyID>
                            </cac:PartyLegalEntity>
                        </cac:Party>
                    </cac:AccountingCustomerParty>'''
            else:
                AccountingCustomerPartyXML=f'''
                <cac:AccountingCustomerParty>
                    <cac:Party>
                        <cac:PostalAddress>
                            <cbc:StreetName>{str(df_fact_curenta["Street"].iloc[0])}</cbc:StreetName>
                            <cbc:CityName>{str(df_fact_curenta["City"].iloc[0])}</cbc:CityName> 
                            <cbc:CountrySubentity>RO-{df_fact_curenta["CodRegiune"].iloc[0]}</cbc:CountrySubentity>
                            <cac:Country>
                                <cbc:IdentificationCode>{str(df_fact_curenta["Country"].iloc[0])}</cbc:IdentificationCode>
                            </cac:Country>
                        </cac:PostalAddress>
                        <cac:PartyTaxScheme>
                            <cbc:CompanyID>{str(df_fact_curenta["SI_VATRegNo"].iloc[0])}</cbc:CompanyID>
                            <cac:TaxScheme>
                                <cbc:ID>VAT</cbc:ID>
                            </cac:TaxScheme>
                        </cac:PartyTaxScheme>
                        <cac:PartyLegalEntity>
                            <cbc:RegistrationName>{str(df_fact_curenta["Name"].iloc[0])}</cbc:RegistrationName>
                            <cbc:CompanyID>{str(df_fact_curenta["SI_VATRegNo"].iloc[0])}</cbc:CompanyID>
                        </cac:PartyLegalEntity>
                    </cac:Party>
                </cac:AccountingCustomerParty>'''
            # invoiceLine += xml_efactura + AccountingCustomerPartyXML 
            # Variabilă pentru a număra elementele din fiecare factură
            invoiceLine = ""
            line_count = 1
            total_tva=0
            # print(subtotalTva)
            # <cbc:ID>{row["ID TVA"]}</cbc:ID>
            TAXTOTAL="\n<cac:TaxTotal>\n"
            TaxTotal =""
            for index, row in subtotalTva.iterrows():
                taxamount=subtotalTvaValuta["Valoare linia TVA (Valuta)"][index].sum()
                taxamounttotal=subtotalTvaValuta["Valoare linia TVA (Valuta)"].sum()
                taxamounttotalLEI=subtotalTvaLEI["Valoare linia TVA"].sum()
                taxamounttotal=normal_round(taxamounttotal, decimals=2)
                taxamounttotalLEI=normal_round(taxamounttotalLEI, decimals=2)
                bazaV = subtotalBazaValuta["SI_Amount_Valuta"][index].sum()
                baza= subtotalBaza["SI_Amount"][index].sum()
                baza=normal_round(baza, decimals=2)
                bazaV=normal_round(bazaV, decimals=2)
                taxamount=normal_round(taxamount, decimals=2)

                if str(subtotalIDTVA["ID TVA"][index])=="AE":

                    TaxExemptionReasonCode="VATEX-EU-AE"
                    TaxTotal = TaxTotal+f'''
                    
                        
                        <cac:TaxSubtotal>
                            <cbc:TaxableAmount currencyID="{str(currency)}">{str(round(float(str(bazaV)),2))}</cbc:TaxableAmount>
                            <cbc:TaxAmount currencyID="{str(currency)}">{str(round(float(str(row["Valoare linia TVA (Valuta)"])),2))}</cbc:TaxAmount>
                            <cac:TaxCategory>
                                <cbc:ID>{subtotalIDTVA["ID TVA"][index]}</cbc:ID>
                                <cbc:Percent>{str(round(float(str(row["Cota"])),2))}</cbc:Percent>
                                <cbc:TaxExemptionReasonCode>{TaxExemptionReasonCode}</cbc:TaxExemptionReasonCode>
                                <cac:TaxScheme>
                                    <cbc:ID>VAT</cbc:ID>
                                </cac:TaxScheme>
                            </cac:TaxCategory>
                        </cac:TaxSubtotal>
                    \n'''
                else:
                    TaxTotal = TaxTotal + f'''

                        <cac:TaxSubtotal>
                                <cbc:TaxableAmount currencyID="{str(currency)}">{str(round(float(str(bazaV)),2))}</cbc:TaxableAmount>
                                <cbc:TaxAmount currencyID="{str(currency)}">{str(round(float(str(row["Valoare linia TVA (Valuta)"])),2))}</cbc:TaxAmount>
                                <cac:TaxCategory>
                                    <cbc:ID>{subtotalIDTVA["ID TVA"][index]}</cbc:ID>
                                    <cbc:Percent>{str(round(float(str(row["Cota"])),2))}</cbc:Percent>
                                    <cac:TaxScheme>
                                        <cbc:ID>VAT</cbc:ID>
                                    </cac:TaxScheme>
                                </cac:TaxCategory>
                        </cac:TaxSubtotal>
                    \n'''
                    # print("abc")
            TAXTOTAL = TAXTOTAL + '<cbc:TaxAmount currencyID="RON">' + str(round(float(str(taxamounttotalLEI)),2)) +'</cbc:TaxAmount>' + "\n</cac:TaxTotal>\n"+ TAXTOTAL + '<cbc:TaxAmount currencyID="'+str(currency)+'">' + str(round(float(str(taxamounttotal)),2)) +'</cbc:TaxAmount>' + TaxTotal + "\n</cac:TaxTotal>\n"
            for index, row in df_fact_curenta.iterrows():
                line_amount = row["Foreign Amount"]
                currency=row["Foreign Currency"]
                # line_amount=normal_round(line_amount, decimals=2)
                val_cu_tva = row["Valoare linie cu TVA (Valuta)"]
                tva = row["Valoare linia TVA (Valuta)"]
                # tva = normal_round(tva, decimals=2)
                
                total_tva += val_cu_tva
                tva_total += tva
                
                total_amount += line_amount
                # total_amount=normal_round(total_amount, decimals=2)
                invoiceLine += f'''<cac:InvoiceLine>
                        <cbc:ID>{line_count}</cbc:ID>
                        <cbc:InvoicedQuantity unitCode="{row["Cod Unitate Masura"]}">{row["Quantity"]}</cbc:InvoicedQuantity>
                        <cbc:LineExtensionAmount currencyID="{str(row["SI_Amount_Valuta"])}">{str(round(float(str(row["SI_Amount_Valuta"])),2))}</cbc:LineExtensionAmount>
                        <cac:Item>
                            <cbc:Name>{row["SI_Description"]}</cbc:Name>
                            <cac:ClassifiedTaxCategory>
                                <cbc:ID>{row["ID TVA"]}</cbc:ID>
                                <cbc:Percent>{str(round(float(str(row["SI_VatPerc"])),2))}</cbc:Percent>
                                <cac:TaxScheme>
                                    <cbc:ID>VAT</cbc:ID>
                                </cac:TaxScheme>
                            </cac:ClassifiedTaxCategory>
                        </cac:Item>
                        <cac:Price>
                            <cbc:PriceAmount currencyID="{str(row["SI_CurrencyCode"])}">{str(abs(round(float(str(row["SI_Amount_Valuta"])),2)))}</cbc:PriceAmount>
                        </cac:Price>
                    </cac:InvoiceLine>'''
                    
                
                
                # Incrementați numărul elementului pentru următoarea linie din factură
                line_count += 1
            tva_total = normal_round(tva_total, decimals = 2)
            total_amount_with_vat = total_amount + tva_total
            # total_amount_with_vat=normal_round(total_amount_with_vat, decimals=2)
            # print(row["Journal"], total_tva)
            # print(str(df_fact_curenta["Journal"].iloc[0]).replace(".0", "") ,total_amount_without_vat)

            PaymentMeans = f'''
                <cac:PaymentMeans>
                    <cbc:PaymentMeansCode>10</cbc:PaymentMeansCode>
                    <cac:PayeeFinancialAccount>
                        <cbc:ID>{df_fact_curenta["SI_BankAccNo"].iloc[0]}</cbc:ID>
                        <cbc:Name>{df_fact_curenta["SI_BankName"].iloc[0]}</cbc:Name>
                        <cac:FinancialInstitutionBranch>
                            <cbc:ID>{df_fact_curenta["SI_BankSwiftCode"].iloc[0]}</cbc:ID>
                        </cac:FinancialInstitutionBranch>
                    </cac:PayeeFinancialAccount>
                </cac:PaymentMeans>'''

            LegalMonetary = f'''
            <cac:LegalMonetaryTotal>
                <cbc:LineExtensionAmount currencyID="{str(currency)}">{str(round(float(str(total_amount)),2))}</cbc:LineExtensionAmount>
                <cbc:TaxExclusiveAmount currencyID="{str(currency)}">{str(round(float(str(total_amount)),2))}</cbc:TaxExclusiveAmount>
                <cbc:TaxInclusiveAmount currencyID="{str(currency)}">{str(round(float(str(total_amount_with_vat)),2))}</cbc:TaxInclusiveAmount>
                <cbc:AllowanceTotalAmount currencyID="{str(currency)}">0.00</cbc:AllowanceTotalAmount>
                <cbc:ChargeTotalAmount currencyID="{str(currency)}">0.00</cbc:ChargeTotalAmount>
                <cbc:PrepaidAmount currencyID="{str(currency)}">0.00</cbc:PrepaidAmount>
                <cbc:PayableRoundingAmount currencyID="{str(currency)}">0.00</cbc:PayableRoundingAmount>
                <cbc:PayableAmount currencyID="{str(currency)}">{str(round(float(str(total_amount_with_vat)),2))}</cbc:PayableAmount>
            </cac:LegalMonetaryTotal>'''


            # print(total_amount)
            # eFacturaXML = meta + XML_Header + AccountingSupplierParty + AccountingCustomerPartyXML + " TAX TOTAL " + " LEGAL MONETARY TOOL " + invoiceLine +"</Invoice>"
            # Scrieți fișierul XML pentru fiecare factură în parte
            eFacturaXML = XML_Header + AccountingSupplierParty + AccountingCustomerPartyXML + PaymentMeans + TAXTOTAL + LegalMonetary + invoiceLine +"\n</Invoice>"
            def remove_diacritics(input_str):
                nfkd_form = unicodedata.normalize('NFKD', input_str)
                return ''.join([c for c in nfkd_form if not unicodedata.combining(c)])

            eFacturaXML = remove_diacritics(eFacturaXML)
            eFacturaXML=eFacturaXML.replace("&"," ")

            # Scrie conținutul în fișierul XML
            with io.open(f"C:/Dezvoltare/E-Factura/2023/eFactura/Konica/eFacturaKonicaMinolta/outs/SalesInvoiceValuta_{str(listaNumarFact[i]).replace('.0', '')}.xml", "w", encoding="utf-8") as f:
                f.write(eFacturaXML)
                
            
if "SalesCrMemoHeader" in excel_file.sheet_names:
    for i in range(0, len(listaNumarFactCM)):
        df_fact_curenta = CreditMemo_EFACTURA.groupby(["SC_DocNo"]).get_group(listaNumarFactCM[i])
        issue_date = pd.to_datetime(df_fact_curenta["SC_DocumentDate"], format='%d/%m/%Y').dt.strftime('%Y-%m-%d').iloc[0]
        data_scadenta=pd.to_datetime(df_fact_curenta["SC_DueDate"], format='%d/%m/%Y').dt.strftime('%Y-%m-%d').iloc[0]
        
        listaCote = list(set(list(df_fact_curenta["SC_VATPerc"])))
        # issue_date = pd.to_datetime(df_fact_curenta["Inv. Date"]).dt.strftime('%Y-%m-%d').iloc[0]
        # data_scadenta=pd.to_datetime(df_fact_curenta["SC_DueDate"]).dt.strftime('%Y-%m-%d').iloc[0]
        subtotalTva = df_fact_curenta.groupby("SC_VATPerc")["Valoare linia TVA"].sum().reset_index()
        subtotalBaza=df_fact_curenta.groupby("SC_VATPerc")["SC_Amount"].sum().reset_index()
        subtotalIDTVA=df_fact_curenta.groupby("ID TVA")["SC_VATPerc"].sum().reset_index()
        
        if str(df_fact_curenta["SC_CurrencyCode"].iloc[0])=="RON":

        
            total_amount = 0

            XML_Header = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n
            <CreditNote\nxmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2" 
        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
        xmlns="urn:oasis:names:specification:ubl:schema:xsd:CreditNote-2">

        <cbc:CustomizationID>urn:cen.eu:en16931:2017#compliant#urn:efactura.mfinante.ro:CIUS-RO:1.0.1</cbc:CustomizationID>
            <cbc:ID>{str(df_fact_curenta["SC_DocNo"].iloc[0]).replace(".0", "")}</cbc:ID>
            <cbc:IssueDate>{issue_date}</cbc:IssueDate>
            
            <cbc:CreditNoteTypeCode>381</cbc:CreditNoteTypeCode>
            <cbc:Note>Sell-to-Contact:{str(df_fact_curenta["SC_SellToContact"].iloc[0])}</cbc:Note>
            <cbc:Note>Your Ref. No:{str(df_fact_curenta["SC_ExternalDocNo"].iloc[0])}</cbc:Note>
            <cbc:Note>Salesperson Code:{str(df_fact_curenta["SC_SalespersonCode"].iloc[0])}</cbc:Note>
            <cbc:Note>{df_fact_curenta["SC_RemittanceDetails"].iloc[0]}</cbc:Note>
            <cbc:Note>Project No.: {df_fact_curenta["SC_ProjectNo"].iloc[0]}</cbc:Note>
                
            <cbc:DocumentCurrencyCode>RON</cbc:DocumentCurrencyCode>
            '''

            AccountingSupplierParty = '''
            <cac:AccountingSupplierParty>
                <cac:Party>
                    <cac:PostalAddress>
                        <cbc:StreetName>'''+str(strada)+'''</cbc:StreetName>
                        <cbc:CityName>'''+str(oras)+'''</cbc:CityName>
                        <cbc:CountrySubentity>'''+str(countrySubentity)+'''</cbc:CountrySubentity>
                        <cac:Country>
                            <cbc:IdentificationCode>'''+str(country)+'''</cbc:IdentificationCode>
                        </cac:Country>
                    </cac:PostalAddress>
                    <cac:PartyTaxScheme>
                        <cbc:CompanyID>'''+str(vatID)+'''</cbc:CompanyID>
                        <cac:TaxScheme>
                            <cbc:ID>VAT</cbc:ID>
                        </cac:TaxScheme>
                    </cac:PartyTaxScheme>
                    <cac:PartyLegalEntity>
                        <cbc:RegistrationName>'''+str(numeCompanie)+'''</cbc:RegistrationName>
                        <cbc:CompanyID>'''+str(vatID)+'''</cbc:CompanyID>
                    </cac:PartyLegalEntity>
                </cac:Party>
            </cac:AccountingSupplierParty>
            '''
            if str(df_fact_curenta["Street"].iloc[0]) == "  ":
                AccountingCustomerPartyXML=f'''
                    <cac:AccountingCustomerParty>
                        <cac:Party>
                            <cac:PostalAddress>
                                <cbc:StreetName>{str(df_fact_curenta["City"].iloc[0])}</cbc:StreetName>
                                <cbc:CityName>{str(df_fact_curenta["City"].iloc[0])}</cbc:CityName>
                                <cbc:CountrySubentity>RO-{df_fact_curenta["CodRegiune"].iloc[0]}</cbc:CountrySubentity>
                                <cac:Country>
                                    <cbc:IdentificationCode>{str(df_fact_curenta["Country"].iloc[0])}</cbc:IdentificationCode>
                                </cac:Country>
                            </cac:PostalAddress>
                            <cac:PartyTaxScheme>
                                <cbc:CompanyID>{str(df_fact_curenta["SC_VATRegNo"].iloc[0])}</cbc:CompanyID>
                                <cac:TaxScheme>
                                    <cbc:ID>VAT</cbc:ID>
                                </cac:TaxScheme>
                            </cac:PartyTaxScheme>
                            <cac:PartyLegalEntity>
                                <cbc:RegistrationName>{str(df_fact_curenta["Name"].iloc[0])}</cbc:RegistrationName>
                                <cbc:CompanyID>{str(df_fact_curenta["SC_VATRegNo"].iloc[0])}</cbc:CompanyID>
                            </cac:PartyLegalEntity>
                        </cac:Party>
                    </cac:AccountingCustomerParty>'''
            else:
                AccountingCustomerPartyXML=f'''
                <cac:AccountingCustomerParty>
                    <cac:Party>
                        <cac:PostalAddress>
                            <cbc:StreetName>{str(df_fact_curenta["Street"].iloc[0])}</cbc:StreetName>
                            <cbc:CityName>{str(df_fact_curenta["City"].iloc[0])}</cbc:CityName> 
                            <cbc:CountrySubentity>RO-{df_fact_curenta["CodRegiune"].iloc[0]}</cbc:CountrySubentity>
                            <cac:Country>
                                <cbc:IdentificationCode>{str(df_fact_curenta["Country"].iloc[0])}</cbc:IdentificationCode>
                            </cac:Country>
                        </cac:PostalAddress>
                        <cac:PartyTaxScheme>
                            <cbc:CompanyID>{str(df_fact_curenta["SC_VATRegNo"].iloc[0])}</cbc:CompanyID>
                            <cac:TaxScheme>
                                <cbc:ID>VAT</cbc:ID>
                            </cac:TaxScheme>
                        </cac:PartyTaxScheme>
                        <cac:PartyLegalEntity>
                            <cbc:RegistrationName>{str(df_fact_curenta["Name"].iloc[0])}</cbc:RegistrationName>
                            <cbc:CompanyID>{str(df_fact_curenta["SC_VATRegNo"].iloc[0])}</cbc:CompanyID>
                        </cac:PartyLegalEntity>
                    </cac:Party>
                </cac:AccountingCustomerParty>'''
                
            # invoiceLine += xml_efactura + AccountingCustomerPartyXML 
            # Variabilă pentru a număra elementele din fiecare factură
            invoiceLine = ""
            line_count = 1
            total_tva=0
            # print(subtotalTva)
            # <cbc:ID>{row["ID TVA"]}</cbc:ID>
            for index, row in subtotalTva.iterrows():
                taxamount=subtotalTva["Valoare linia TVA"].sum()
                baza = subtotalBaza["SC_Amount"].sum()
                taxamount = normal_round(taxamount, decimals=2)
                taxamount2 = row["Valoare linia TVA"]
                taxamount2 = normal_round(taxamount2, decimals=2)
                if subtotalIDTVA["ID TVA"][index]=="S":
                    TaxTotal = f'''
                    <cac:TaxTotal>
                        <cbc:TaxAmount currencyID="RON">{(str(abs(taxamount)))}</cbc:TaxAmount>
                        <cac:TaxSubtotal>
                            <cbc:TaxableAmount currencyID="RON">{str(abs(round(float(str(baza)),2)))}</cbc:TaxableAmount>
                            <cbc:TaxAmount currencyID="RON">{(str(abs(taxamount2)))}</cbc:TaxAmount>
                            <cac:TaxCategory>
                                
                                <cbc:ID>{subtotalIDTVA["ID TVA"][index]}</cbc:ID>
                                <cbc:Percent>{str(round(float(str(row["SC_VATPerc"])),2))}</cbc:Percent>
                                <cac:TaxScheme>
                                    <cbc:ID>VAT</cbc:ID>
                                </cac:TaxScheme>
                            </cac:TaxCategory>
                        </cac:TaxSubtotal>
                    </cac:TaxTotal>\n'''
                else:
                    TaxExemptionReasonCode="VATEX-EU-AE"
                    TaxTotal = f'''
                    <cac:TaxTotal>
                        <cbc:TaxAmount currencyID="RON">{(str(abs(taxamount)))}</cbc:TaxAmount>
                        <cac:TaxSubtotal>
                            <cbc:TaxableAmount currencyID="RON">{str(abs(round(float(str(baza)),2)))}</cbc:TaxableAmount>
                            <cbc:TaxAmount currencyID="RON">{(str(taxamount2))}</cbc:TaxAmount>
                            <cac:TaxCategory>
                                
                                <cbc:ID>{subtotalIDTVA["ID TVA"][index]}</cbc:ID>

                                <cbc:Percent>{str(round(float(str(row["SC_VATPerc"])),2))}</cbc:Percent>
                                <cbc:TaxExemptionReasonCode>{TaxExemptionReasonCode}</cbc:TaxExemptionReasonCode>
                                <cac:TaxScheme>
                                    <cbc:ID>VAT</cbc:ID>
                                </cac:TaxScheme>
                            </cac:TaxCategory>
                        </cac:TaxSubtotal>
                    </cac:TaxTotal>\n'''
                
            
            for index, row in df_fact_curenta.iterrows():
                line_amount = row["SC_Amount"]
                val_cu_tva = row["Valoare linie cu TVA"]
                
                total_tva += val_cu_tva
                total_amount += line_amount
                invoiceLine += f'''<cac:CreditNoteLine>
                        <cbc:ID>{line_count}</cbc:ID>
                        <cbc:CreditedQuantity unitCode="{row["Cod Unitate Masura"]}">{abs(row["SC_Quantity"])}</cbc:CreditedQuantity>
                        <cbc:LineExtensionAmount currencyID="RON">{str(abs(round(float(str(row["SC_Amount"])),2)))}</cbc:LineExtensionAmount>
                        <cac:Item>
                            <cbc:Name>{row["SC_Description"]}</cbc:Name>
                            <cac:ClassifiedTaxCategory>
                                <cbc:ID>{row["ID TVA"]}</cbc:ID>
                                <cbc:Percent>{str(round(float(str(row["SC_VATPerc"])),2))}</cbc:Percent>
                                <cac:TaxScheme>
                                    <cbc:ID>VAT</cbc:ID>
                                </cac:TaxScheme>
                            </cac:ClassifiedTaxCategory>
                        </cac:Item>
                        <cac:Price>
                            <cbc:PriceAmount currencyID="RON">{str(abs(round(float(str(row["Pret Unitar"])),2)))}</cbc:PriceAmount>
                        </cac:Price>
                    </cac:CreditNoteLine>'''
                    
                
                
                # Incrementați numărul elementului pentru următoarea linie din factură
                line_count += 1
            # total_amount_with_vat = total_amount * (1 + row["Cota"] / 100)
            # total_amount_with_vat=normal_round(total_amount_with_vat,)
            total_amount_with_vat=normal_round(total_amount, decimals=2)+normal_round(taxamount2, decimals=2)
            # print(row["Inv. No"], total_tva)
            # print(str(df_fact_curenta["Inv. No"].iloc[0]).replace(".0", "") ,total_amount_without_vat)
            
            PaymentMeans = f'''
            <cac:PaymentMeans>
                <cbc:PaymentMeansCode>10</cbc:PaymentMeansCode>
                <cac:PayeeFinancialAccount>
                        <cbc:ID>{df_fact_curenta["SC_BankAccNo"].iloc[0]}</cbc:ID>
                        <cbc:Name>{df_fact_curenta["SC_BankName"].iloc[0]}</cbc:Name>
                        <cac:FinancialInstitutionBranch>
                            <cbc:ID>{df_fact_curenta["SC_BankSwiftCode"].iloc[0]}</cbc:ID>
                        </cac:FinancialInstitutionBranch>
                    </cac:PayeeFinancialAccount>
            </cac:PaymentMeans>'''

            
            LegalMonetary = f'''
            <cac:LegalMonetaryTotal>
                <cbc:LineExtensionAmount currencyID="RON">{str(abs(round(float(str(total_amount)),2)))}</cbc:LineExtensionAmount>
                <cbc:TaxExclusiveAmount currencyID="RON">{str(abs(round(float(str(total_amount)),2)))}</cbc:TaxExclusiveAmount>
                <cbc:TaxInclusiveAmount currencyID="RON">{str(abs(round(float(str(total_amount_with_vat)),2)))}</cbc:TaxInclusiveAmount>
                <cbc:AllowanceTotalAmount currencyID="RON">0.00</cbc:AllowanceTotalAmount>
                <cbc:ChargeTotalAmount currencyID="RON">0.00</cbc:ChargeTotalAmount>
                <cbc:PrepaidAmount currencyID="RON">0.00</cbc:PrepaidAmount>
                <cbc:PayableRoundingAmount currencyID="RON">0.00</cbc:PayableRoundingAmount>
                <cbc:PayableAmount currencyID="RON">{str(abs(round(float(str(total_amount_with_vat)),2)))}</cbc:PayableAmount>
            </cac:LegalMonetaryTotal>'''
            eFacturaXML = XML_Header + AccountingSupplierParty + AccountingCustomerPartyXML + PaymentMeans + TaxTotal +LegalMonetary + invoiceLine +"\n</CreditNote>"
            def remove_diacritics(input_str):
                nfkd_form = unicodedata.normalize('NFKD', input_str)
                return ''.join([c for c in nfkd_form if not unicodedata.combining(c)])

            eFacturaXML = remove_diacritics(eFacturaXML)
            eFacturaXML=eFacturaXML.replace("&"," ")

            # Scrie conținutul în fișierul XML
            with io.open(f"C:/Dezvoltare/E-Factura/2023/eFactura/Konica/eFacturaKonicaMinolta/outs/SalesCreditNote_{str(listaNumarFactCM[i]).replace('.0', '')}.xml", "w", encoding="utf-8") as f:
                f.write(eFacturaXML)
            # with io.open(f"/home/efactura/efactura_expeditors/outs/SalesCreditNoteValuta_{str(listaNumarFact[i]).replace('.0', '')}.xml", "w", encoding="utf-8") as f:
            #     f.write(eFacturaXML)

            print("A PRELUCRAT DATELE")
        else:
            df_fact_curenta = CreditMemo_EFACTURA.groupby(["SC_DocNo"]).get_group(listaNumarFactCM[i])
            issue_date = pd.to_datetime(df_fact_curenta["SC_DocumentDate"], format='%d/%m/%Y').dt.strftime('%Y-%m-%d').iloc[0]
            data_scadenta=pd.to_datetime(df_fact_curenta["SC_DueDate"], format='%d/%m/%Y').dt.strftime('%Y-%m-%d').iloc[0]
            
            listaCote = list(set(list(df_fact_curenta["SC_VATPerc"])))
            currency=str(df_fact_curenta["SC_CurrencyCode"].iloc[0])
            
            listaCote = list(set(list(df_fact_curenta["SC_VatPerc"])))
            subtotalTvaLEI=df_fact_curenta.groupby("SC_VatPerc")["Valoare linia TVA"].sum().reset_index()
            subtotalTva = df_fact_curenta.groupby("SC_VatPerc")["Valoare linia TVA (Valuta)"].sum().reset_index()
            subtotalBaza=df_fact_curenta.groupby("SC_VatPerc")["Amount"].sum().reset_index()
            subtotalBazaValuta=df_fact_curenta.groupby("SC_VatPerc")["SC_Amount_Valuta"].sum().reset_index()
            subtotalTvaValuta=df_fact_curenta.groupby("SC_VatPerc")["Valoare linia TVA (Valuta)"].sum().reset_index()
            subtotalIDTVA=df_fact_curenta.groupby("ID TVA")["SC_VatPerc"].sum().reset_index()
            
            total_amount = 0
            tva_total=0
            creditNoteId2 = str(df_fact_curenta["SC_DocNo"].iloc[0]).replace(".0", "")
            if creditNoteId2.isdigit():
                creditNoteId2 = int(creditNoteId2)
            

            XML_Header = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n
            <CreditNote\nxmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2" 
        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
        xmlns="urn:oasis:names:specification:ubl:schema:xsd:CreditNote-2">
        
        <cbc:CustomizationID>urn:cen.eu:en16931:2017#compliant#urn:efactura.mfinante.ro:CIUS-RO:1.0.1</cbc:CustomizationID>
            <cbc:ID>{creditNoteId2}</cbc:ID>
            <cbc:IssueDate>{issue_date}</cbc:IssueDate>
            
            <cbc:CreditNoteTypeCode>381</cbc:CreditNoteTypeCode>
            <cbc:Note>Sell-to-Contact:{str(df_fact_curenta["SI_SellToContact"].iloc[0])}</cbc:Note>
            <cbc:Note>Your Ref. No:{str(df_fact_curenta["SI_ExternalDocNo"].iloc[0])}</cbc:Note>
            <cbc:Note>Salesperson Code:{str(df_fact_curenta["SI_SalespersonCode"].iloc[0])}</cbc:Note>
            <cbc:Note>{df_fact_curenta["SI_RemittanceDetails"].iloc[0]}</cbc:Note>
            <cbc:Note>Project No.: {df_fact_curenta["SI_ProjectNo"].iloc[0]}</cbc:Note>
            <cbc:DocumentCurrencyCode>{str(df_fact_curenta['SC_CurrencyCode'].iloc[0])}</cbc:DocumentCurrencyCode>
            <cbc:TaxCurrencyCode>RON</cbc:TaxCurrencyCode>
            '''

            AccountingSupplierParty = '''
            <cac:AccountingSupplierParty>
                <cac:Party>
                    <cac:PostalAddress>
                        <cbc:StreetName>'''+str(strada)+'''</cbc:StreetName>
                        <cbc:CityName>'''+str(oras)+'''</cbc:CityName>
                        <cbc:CountrySubentity>'''+str(countrySubentity)+'''</cbc:CountrySubentity>
                        <cac:Country>
                            <cbc:IdentificationCode>'''+str(country)+'''</cbc:IdentificationCode>
                        </cac:Country>
                    </cac:PostalAddress>
                    <cac:PartyTaxScheme>
                        <cbc:CompanyID>'''+str(vatID)+'''</cbc:CompanyID>
                        <cac:TaxScheme>
                            <cbc:ID>VAT</cbc:ID>
                        </cac:TaxScheme>
                    </cac:PartyTaxScheme>
                    <cac:PartyLegalEntity>
                        <cbc:RegistrationName>'''+str(numeCompanie)+'''</cbc:RegistrationName>
                        <cbc:CompanyID>'''+str(vatID)+'''</cbc:CompanyID>
                    </cac:PartyLegalEntity>
                </cac:Party>
            </cac:AccountingSupplierParty>
            '''
            
            if str(df_fact_curenta["Street"].iloc[0]) == "  ":
                AccountingCustomerPartyXML=f'''
                    <cac:AccountingCustomerParty>
                        <cac:Party>
                            <cac:PostalAddress>
                                <cbc:StreetName>{str(df_fact_curenta["City"].iloc[0])}</cbc:StreetName>
                                <cbc:CityName>{str(df_fact_curenta["City"].iloc[0])}</cbc:CityName>
                                <cbc:CountrySubentity>RO-{df_fact_curenta["CodRegiune"].iloc[0]}</cbc:CountrySubentity>
                                <cac:Country>
                                    <cbc:IdentificationCode>{str(df_fact_curenta["Country"].iloc[0])}</cbc:IdentificationCode>
                                </cac:Country>
                            </cac:PostalAddress>
                            <cac:PartyTaxScheme>
                                <cbc:CompanyID>{str(df_fact_curenta["SC_VATRegNo"].iloc[0])}</cbc:CompanyID>
                                <cac:TaxScheme>
                                    <cbc:ID>VAT</cbc:ID>
                                </cac:TaxScheme>
                            </cac:PartyTaxScheme>
                            <cac:PartyLegalEntity>
                                <cbc:RegistrationName>{str(df_fact_curenta["Name"].iloc[0])}</cbc:RegistrationName>
                                <cbc:CompanyID>{str(df_fact_curenta["SC_VATRegNo"].iloc[0])}</cbc:CompanyID>
                            </cac:PartyLegalEntity>
                        </cac:Party>
                    </cac:AccountingCustomerParty>'''
            else:
                AccountingCustomerPartyXML=f'''
                <cac:AccountingCustomerParty>
                    <cac:Party>
                        <cac:PostalAddress>
                            <cbc:StreetName>{str(df_fact_curenta["Street"].iloc[0])}</cbc:StreetName>
                            <cbc:CityName>{str(df_fact_curenta["City"].iloc[0])}</cbc:CityName> 
                            <cbc:CountrySubentity>RO-{df_fact_curenta["CodRegiune"].iloc[0]}</cbc:CountrySubentity>
                            <cac:Country>
                                <cbc:IdentificationCode>{str(df_fact_curenta["Country"].iloc[0])}</cbc:IdentificationCode>
                            </cac:Country>
                        </cac:PostalAddress>
                        <cac:PartyTaxScheme>
                            <cbc:CompanyID>{str(df_fact_curenta["SC_VATRegNo"].iloc[0])}</cbc:CompanyID>
                            <cac:TaxScheme>
                                <cbc:ID>VAT</cbc:ID>
                            </cac:TaxScheme>
                        </cac:PartyTaxScheme>
                        <cac:PartyLegalEntity>
                            <cbc:RegistrationName>{str(df_fact_curenta["Name"].iloc[0])}</cbc:RegistrationName>
                            <cbc:CompanyID>{str(df_fact_curenta["SC_VATRegNo"].iloc[0])}</cbc:CompanyID>
                        </cac:PartyLegalEntity>
                    </cac:Party>
                </cac:AccountingCustomerParty>'''
            # invoiceLine += xml_efactura + AccountingCustomerPartyXML 
            # Variabilă pentru a număra elementele din fiecare factură
            invoiceLine = ""
            line_count = 1
            total_tva=0
            # print(subtotalTva)
            # <cbc:ID>{row["ID TVA"]}</cbc:ID>
            TAXTOTAL="\n<cac:TaxTotal>\n"
            TaxTotal =""
            for index, row in subtotalTva.iterrows():
                taxamount=subtotalTvaValuta["Valoare linia TVA (Valuta)"][index].sum()
                taxamounttotal=subtotalTvaValuta["Valoare linia TVA (Valuta)"].sum()
                taxamounttotalLEI=subtotalTvaLEI["Valoare linia TVA"].sum()
                taxamounttotal=normal_round(taxamounttotal, decimals=2)
                taxamount=normal_round(taxamount, decimals=2)
                taxamounttotalLEI=normal_round(taxamounttotalLEI, decimals=2)
                bazaV = subtotalBazaValuta["SC_Amount_Valuta"][index].sum()
                baza= subtotalBaza["SC_Amount"][index].sum()
                # baza=normal_round(baza, decimals=2)
                # bazaV=normal_round(bazaV, decimals=2)

                if str(subtotalIDTVA["ID TVA"][index])=="AE":

                    TaxExemptionReasonCode="VATEX-EU-AE"
                    TaxTotal = TaxTotal+f'''
                    
                        
                        <cac:TaxSubtotal>
                            <cbc:TaxableAmount currencyID="{str(currency)}">{str(round(float(str(bazaV)),2))}</cbc:TaxableAmount>
                            <cbc:TaxAmount currencyID="{str(currency)}">{str(round(float(str(row["Valoare linia TVA (Valuta)"])),2))}</cbc:TaxAmount>
                            <cac:TaxCategory>
                                <cbc:ID>{subtotalIDTVA["ID TVA"][index]}</cbc:ID>
                                <cbc:Percent>{str(round(float(str(row["SC_VatPerc"])),2))}</cbc:Percent>
                                <cbc:TaxExemptionReasonCode>{TaxExemptionReasonCode}</cbc:TaxExemptionReasonCode>
                                <cac:TaxScheme>
                                    <cbc:ID>VAT</cbc:ID>
                                </cac:TaxScheme>
                            </cac:TaxCategory>
                        </cac:TaxSubtotal>
                    \n'''
                else:
                    TaxTotal = TaxTotal + f'''

                        <cac:TaxSubtotal>
                                <cbc:TaxableAmount currencyID="{str(currency)}">{str(round(float(str(bazaV)),2))}</cbc:TaxableAmount>
                                <cbc:TaxAmount currencyID="{str(currency)}">{str(round(float(str(row["Valoare linia TVA (Valuta)"])),2))}</cbc:TaxAmount>
                                <cac:TaxCategory>
                                    <cbc:ID>{subtotalIDTVA["ID TVA"][index]}</cbc:ID>
                                    <cbc:Percent>{str(round(float(str(row["SC_VatPerc"])),2))}</cbc:Percent>
                                    <cac:TaxScheme>
                                        <cbc:ID>VAT</cbc:ID>
                                    </cac:TaxScheme>
                                </cac:TaxCategory>
                        </cac:TaxSubtotal>
                    \n'''
                    # print("abc")
            TAXTOTAL = TAXTOTAL + '<cbc:TaxAmount currencyID="RON">' + str(round(float(str(taxamounttotalLEI)),2)) +'</cbc:TaxAmount>' + "\n</cac:TaxTotal>\n"+ TAXTOTAL + '<cbc:TaxAmount currencyID="'+str(currency)+'">' + str(round(float(str(taxamounttotal)),2)) +'</cbc:TaxAmount>' + TaxTotal + "\n</cac:TaxTotal>\n"
            for index, row in df_fact_curenta.iterrows():
                line_amount = row["SC_Amount_Valuta"]
                currency=row["SC_CurrencyCode"]
                # line_amount=normal_round(line_amount, decimals=2)
                val_cu_tva = row["Valoare linie cu TVA (Valuta)"]
                tva = row["Valoare linia TVA (Valuta)"]
                # tva = normal_round(tva, decimals=2)
                
                total_tva += val_cu_tva
                tva_total += tva
                total_amount += line_amount
                total_tva=normal_round(total_tva, decimals=2)
                total_amount=normal_round(total_amount, decimals=2)
                invoiceLine += f'''<cac:CreditNoteLine>
                        <cbc:ID>{line_count}</cbc:ID>
                        <cbc:CreditedQuantity unitCode="{row["Cod Unitate Masura"]}">{row["SC_Quantity"]}</cbc:CreditedQuantity>
                        <cbc:LineExtensionAmount currencyID="{str(row["SC_Amount_Valuta"])}">{str(round(float(str(row["SC_Amount_Valuta"])),2))}</cbc:LineExtensionAmount>
                        <cac:Item>
                            <cbc:Name>{row["SC_Description"]}</cbc:Name>
                            <cac:ClassifiedTaxCategory>
                                <cbc:ID>{row["ID TVA"]}</cbc:ID>
                                <cbc:Percent>{str(round(float(str(row["SC_VatPerc"])),2))}</cbc:Percent>
                                <cac:TaxScheme>
                                    <cbc:ID>VAT</cbc:ID>
                                </cac:TaxScheme>
                            </cac:ClassifiedTaxCategory>
                        </cac:Item>
                        <cac:Price>
                            <cbc:PriceAmount currencyID="{str(row["SC_CurrencyCode"])}">{str(abs(round(float(str(row["SC_Amount_Valuta"])),2)))}</cbc:PriceAmount>
                        </cac:Price>
                    </cac:CreditNoteLine>'''
                    
                
                
                # Incrementați numărul elementului pentru următoarea linie din factură
                line_count += 1
            total_amount_with_vat = total_amount + tva_total
            # total_amount_with_vat=normal_round(total_amount_with_vat, decimals=2)
            # print(row["Journal"], total_tva)
            # print(str(df_fact_curenta["Journal"].iloc[0]).replace(".0", "") ,total_amount_without_vat)
            PaymentMeans = f'''
            <cac:PaymentMeans>
                <cbc:PaymentMeansCode>10</cbc:PaymentMeansCode>
                <cac:PayeeFinancialAccount>
                        <cbc:ID>{df_fact_curenta["SC_BankAccNo"].iloc[0]}</cbc:ID>
                        <cbc:Name>{df_fact_curenta["SC_BankName"].iloc[0]}</cbc:Name>
                        <cac:FinancialInstitutionBranch>
                            <cbc:ID>{df_fact_curenta["SC_BankSwiftCode"].iloc[0]}</cbc:ID>
                        </cac:FinancialInstitutionBranch>
                    </cac:PayeeFinancialAccount>
            </cac:PaymentMeans>'''
            


            LegalMonetary = f'''
            <cac:LegalMonetaryTotal>
                <cbc:LineExtensionAmount currencyID="{str(currency)}">{str(round(float(str(total_amount)),2))}</cbc:LineExtensionAmount>
                <cbc:TaxExclusiveAmount currencyID="{str(currency)}">{str(round(float(str(total_amount)),2))}</cbc:TaxExclusiveAmount>
                <cbc:TaxInclusiveAmount currencyID="{str(currency)}">{str(round(float(str(total_amount_with_vat)),2))}</cbc:TaxInclusiveAmount>
                <cbc:AllowanceTotalAmount currencyID="{str(currency)}">0.00</cbc:AllowanceTotalAmount>
                <cbc:ChargeTotalAmount currencyID="{str(currency)}">0.00</cbc:ChargeTotalAmount>
                <cbc:PrepaidAmount currencyID="{str(currency)}">0.00</cbc:PrepaidAmount>
                <cbc:PayableRoundingAmount currencyID="{str(currency)}">0.00</cbc:PayableRoundingAmount>
                <cbc:PayableAmount currencyID="{str(currency)}">{str(round(float(str(total_amount_with_vat)),2))}</cbc:PayableAmount>
            </cac:LegalMonetaryTotal>'''


            # print(total_amount)
            # eFacturaXML = meta + XML_Header + AccountingSupplierParty + AccountingCustomerPartyXML + " TAX TOTAL " + " LEGAL MONETARY TOOL " + invoiceLine +"</Invoice>"
            # Scrieți fișierul XML pentru fiecare factură în parte
            eFacturaXML = XML_Header + AccountingSupplierParty + AccountingCustomerPartyXML + PaymentMeans + TAXTOTAL +LegalMonetary + invoiceLine +"\n</CreditNote>"
            def remove_diacritics(input_str):
                nfkd_form = unicodedata.normalize('NFKD', input_str)
                return ''.join([c for c in nfkd_form if not unicodedata.combining(c)])

            eFacturaXML = remove_diacritics(eFacturaXML)
            eFacturaXML=eFacturaXML.replace("&"," ")

            # Scrie conținutul în fișierul XML
            with io.open(f"C:/Dezvoltare/E-Factura/2023/eFactura/Konica/eFacturaKonicaMinolta/outs/SalesCreditNote_{str(listaNumarFactCM[i]).replace('.0', '')}.xml", "w", encoding="utf-8") as f:
                f.write(eFacturaXML)
            # with io.open(f"/home/efactura/efactura_expeditors/outs/SalesCreditNoteValuta_{str(listaNumarFact[i]).replace('.0', '')}.xml", "w", encoding="utf-8") as f:
            #     f.write(eFacturaXML)

            print("A PRELUCRAT DATELE")

    # print(total_amount)
    # eFacturaXML = meta + XML_Header + AccountingSupplierParty + AccountingCustomerPartyXML + " TAX TOTAL " + " LEGAL MONETARY TOOL " + invoiceLine +"</Invoice>"
    # Scrieți fișierul XML pentru fiecare factură în parte
            # if "CreditNote" in XML_Header:
            #     eFacturaXML = XML_Header + AccountingSupplierParty + AccountingCustomerPartyXML + TaxTotal + LegalMonetary + invoiceLine +"\n</CreditNote>"
            #     def remove_diacritics(input_str):
            #         nfkd_form = unicodedata.normalize('NFKD', input_str)
            #         return ''.join([c for c in nfkd_form if not unicodedata.combining(c)])

            #     eFacturaXML = remove_diacritics(eFacturaXML)
            #     eFacturaXML=eFacturaXML.replace("&", "AND")

            #     # Scrie conținutul în fișierul XML
            #     with open(f"C:/Dezvoltare/E-Factura/2023/eFactura/Konica/eFacturaKonicaMinolta/outs/SalesCreditNote_{str(listaNumarFact[i]).replace('.0', '')}.xml", "w", encoding="utf-8") as f:
            #     # with open(f"/home/efactura/efactura_ferro/outs/CreditNote{str(listaNumarFact[i]).replace('.0', '')}.xml", "w", encoding="utf-8") as f:
            #         f.write(eFacturaXML)
            # else:
            #     eFacturaXML = XML_Header + AccountingSupplierParty + AccountingCustomerPartyXML + TaxTotal + LegalMonetary + invoiceLine +"\n</Invoice>"
            #     def remove_diacritics(input_str):
            #         nfkd_form = unicodedata.normalize('NFKD', input_str)
            #         return ''.join([c for c in nfkd_form if not unicodedata.combining(c)])

            #     eFacturaXML = remove_diacritics(eFacturaXML)
            #     eFacturaXML=eFacturaXML.replace("&", "AND")

            #     # Scrie conținutul în fișierul XML
            #     with open(f"C:/Dezvoltare/E-Factura/2023/eFactura/Konica/eFacturaKonicaMinolta/outs/SalesInvoice_{str(listaNumarFact[i]).replace('.0', '')}.xml", "w", encoding="utf-8") as f:
            #     # with open(f"/home/efactura/efactura_ferro/outs/SalesInvoice_{str(listaNumarFact[i]).replace('.0', '')}.xml", "w", encoding="utf-8") as f:
            #         f.write(eFacturaXML)