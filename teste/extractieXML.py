import xml.etree.ElementTree as ET
from openpyxl import Workbook
 
def xml_to_excel(xml_file, excel_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
 
    wb = Workbook()
 
    document_types = ['SalesCrMemoHeader', 'SelfBillingInvoiceHeader', 'SalesInvoiceHeader']
    line_tags = {'SalesCrMemoHeader': 'SalesCrMemoLine', 'SelfBillingInvoiceHeader': 'SelfBillingInvoiceLine', 'SalesInvoiceHeader': 'SalesInvoiceLine'}
 
    for document_type in document_types:
        ws = wb.create_sheet(title=document_type)
 
        headers = set()
        for element in root.findall('.//' + document_type):
            headers.update(element.attrib.keys())
            for child in element.iter():
                headers.add(child.tag)
        headers_list = list(headers)
        ws.append(headers_list)
 
        header_index_map = {header: index for index, header in enumerate(headers_list)}
 
        for element in root.findall('.//' + document_type):
            header_data = []
            for header in headers_list:
                header_element = element.find('.//' + header)
                if header_element is not None:
                    header_data.append(header_element.text)
                else:
                    header_data.append(None)
 
            line_type = line_tags[document_type]
            for line in element.findall('.//' + line_type):
                row_data = header_data.copy()
                for header in headers_list:
                    if header not in element.attrib:
                        # Folosește findall() pentru a găsi toate elementele copil cu numele header
                        children = line.findall('.//' + header)
                        if children:
                            # Dacă există cel puțin un element copil, concatenăm textele lor
                            text_values = [child.text for child in children if child.text is not None]  # Adaugă doar textele care nu sunt None
                            row_data[header_index_map[header]] = ', '.join(text_values)
                ws.append(row_data)
 
    default_sheet = wb['Sheet']
    wb.remove(default_sheet)
 
    wb.save(excel_file)
 
xml_file = "C:/Dezvoltare/E-Factura/2023/eFactura/Konica/fisierFacturi.xml"
excel_file = "C:/Dezvoltare/E-Factura/2023/eFactura/Konica/eFacturaKonicaMinolta/Baza de date vanzari/output2.xlsx"
xml_to_excel(xml_file, excel_file)