
import pandas as pd
 
# Presupunem că df este DataFrame-ul tău

mandatory_columns = ['col1', 'col2', 'col3', 'col4']
 
# Verificare existență coloane obligatorii

missing_columns = set(mandatory_columns) - set(df.columns)
 
# Afisare mesaj în cazul lipsei de coloane obligatorii

if missing_columns:

    print(f"Eroare: Lipsesc următoarele coloane obligatorii: {', '.join(missing_columns)}")

else:

    print("Toate coloanele obligatorii sunt prezente.")
 
# Verificare valori lipsă în coloanele obligatorii

for column in mandatory_columns:

    missing_values = df[df[column].isnull()]

    if not missing_values.empty:

        print(f"Eroare: Coloana {column} are valori lipsă în rândurile: {missing_values.index.tolist()}")

        # Afișare informații specifice facturii sau numărului de linie

        for index in missing_values.index:

            print(f"  - Factura: {df.at[index, 'InvoiceID']}, Linia: {df.at[index, 'LineID']}")
