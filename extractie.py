import zipfile
import os

directory_path = "C:/Dezvoltare/E-Factura/2023/eFactura/Expeditors/eFacturaExpeditors local/arhive"

# output_directory = 'C:/Dezvoltare/E-Factura/2023/eFactura/Expeditors/eFacturaExpeditors/output conversie'
output_directory = "C:/Dezvoltare/E-Factura/2023/eFactura/Expeditors/eFacturaExpeditors local/outs"
# arhiveANAF = "/home/efactura/efactura_expeditors/arhiveANAF"

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