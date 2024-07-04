import os
import logging
from datetime import datetime

# Aici fac folder pentru log
log_folder = "logs"
os.makedirs(log_folder, exist_ok=True)

# Nume fisier log
log_filename = f"{log_folder}/log_errors_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

# Sterge fisier log daca exista
if os.path.exists(log_filename):
    os.remove(log_filename)

# Creaza un obiect logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

# Adaugă un handler pentru a scrie în fișierul de log doar în cazul erorilor
file_handler = logging.FileHandler(log_filename)
file_handler.setLevel(logging.ERROR)

# Crează un formatter pentru afișarea mesajelor în format specific
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# Adaugă handler-ul la logger
logger.addHandler(file_handler)

# Exemplu de cod care poate genera erori
try:
    # Codul care poate genera erori aici
    result = 1 / 1  # Exemplu de eroare (împărțire la zero)
except Exception as e:
    # Dacă apare o eroare, înregistrează-o în fișierul de log
    logger.error(f"Error: {str(e)}")

# Verifică dacă există erori în fișierul de log și creează un fișier de erori doar dacă există erori
if os.path.getsize(log_filename) > 0:
    print("Există erori. Creare fișier de erori.")
    # Aici poți adăuga cod pentru a face ceva cu fișierul de erori, cum ar fi a trimite un email sau a-l afișa
else:
    print("Nu există erori. Nu este necesar un fișier de erori.")
