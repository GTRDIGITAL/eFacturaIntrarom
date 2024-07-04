import ssl
import datetime
import base64
import smtplib
from flask import session

def trimitereOTPMail(code, destinatari):
    smtp_server = "smtp.office365.com"
    port = 587  # Pentru starttls
    sender_email = "GTRDigital@ro.gt.com"
    password = "g[&vuBR9WQqr=7>D"
    context = ssl.create_default_context()
    message_text = f"Buna ziua,\n\nCodul de autentificare este {code}\n\nThank you,\nGTRDigital"
    
    data = datetime.datetime.now()

    # Adăugați 2 ore
    data_modificata = data + datetime.timedelta(hours=2)

    # Formatați data modificată după nevoie
    data_modificata_formatata = data_modificata.strftime("%d/%m/%Y %H:%M")
    subj = "Cod OTP eFactura" 
    mailTo = destinatari
    


    boundary = "MY_BOUNDARY"

    msg = f"""\
From: {sender_email}
To: {mailTo}
Subject: {subj}
Date: {data_modificata_formatata}
MIME-Version: 1.0
Content-Type: multipart/mixed; boundary={boundary}

--{boundary}
Content-Type: text/plain; charset="utf-8"

{message_text}

"""

    # Încercați să vă conectați la server și să trimiteți e-mailul
    try:
        server = smtplib.SMTP(smtp_server, port)
        server.ehlo() # Poate fi omis
        server.starttls(context=context) # Asigură conexiunea
        server.ehlo() # Poate fi omis
        server.login(sender_email, password)
        server.sendmail(sender_email, mailTo, msg)
    except Exception as e:
        print(e)
    finally:
        server.quit()