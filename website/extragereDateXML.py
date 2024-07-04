import xml.etree.ElementTree as ET
from openpyxl import Workbook

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
excel_file = "C:/Dezvoltare/E-Factura/2023/eFactura/Konica/eFacturaKonicaMinolta/Baza de date vanzari/output.xlsx"
xml_to_excel(xml_file, excel_file)