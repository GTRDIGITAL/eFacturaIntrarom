# Dicționarul cu mesaje
data = {
    'mesaje': [
        {'data_creare': '202403211659', 'cif': '30770893', 'id_solicitare': '4207424572', 'detalii': 'Factura cu id_incarcare=4207424572 emisa de cif_emitent=15417635 pentru cif_beneficiar=30770893', 'tip': 'FACTURA PRIMITA', 'id': '3313849784'},
        {'data_creare': '202403211659', 'cif': '30770893', 'id_solicitare': '4207424792', 'detalii': 'Factura cu id_incarcare=4207424792 emisa de cif_emitent=15417635 pentru cif_beneficiar=30770893', 'tip': 'FACTURA PRIMITA', 'id': '3313849970'},
        {'data_creare': '202403220130', 'cif': '30770893', 'id_solicitare': '4207780446', 'detalii': 'Factura cu id_incarcare=4207780446 emisa de cif_emitent=18692885 pentru cif_beneficiar=30770893', 'tip': 'FACTURA PRIMITA', 'id': '3314497534'},
        # ... alte mesaje ...
    ]
}

# Lista de ID-uri căutate
id_cautat = ['3313849784', '3314497534']

# Filtrarea mesajelor
mesaje_filtrate = [mesaj for mesaj in data['mesaje'] if mesaj['id'] in id_cautat]

# Rezultatul filtrat
print(mesaje_filtrate)
