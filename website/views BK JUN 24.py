from flask import Blueprint, render_template, redirect, request, session, flash, send_file, send_from_directory, url_for, Response, redirect, url_for, session
from flask_login import login_user, login_required, logout_user, current_user
import time
import sqlite3
from flask import jsonify
from threading import Thread
import pyotp
# import mysql.connector
# import jsonify
# from flask import jsonify
from . import db
from .apeluri_efactura import *
from .prelucrareDate import *
from .models import Users
# from .facturiPrimite import *
from .auth import login
from tempfile import NamedTemporaryFile
import json
import smtplib, ssl
import base64
import datetime
import os
import pymysql
from sqlalchemy import create_engine, text
from .trimitereCodOTP import *

def trimitereMail():
    smtp_server = "smtp.office365.com"
    port = 587  # Pentru starttls
    sender_email = "GTRDigital@ro.gt.com"
    password = "g[&vuBR9WQqr=7>D"
    context = ssl.create_default_context()
    message_text = "Yaaaaay\n\nThank you,\nGTRDigital"
    
    date = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    subj = "Facturi SPV " + str(date)
    mailTo = "cristian.iordache@ro.gt.com"
    destinatie = "C:/Dezvoltare/E-Factura/2023/eFactura/Konica/eFacturaKonicaMinolta local/destinatie/"
    # destinatie = '/home/efactura/efactura_konica/destinatie/'
    attachment_path = destinatie+"rezultat.zip"

    with open(attachment_path, "rb") as attachment:
        attachment_data = attachment.read()
        attachment_encoded = base64.b64encode(attachment_data).decode()

    boundary = "MY_BOUNDARY"

    msg = f"""\
From: {sender_email}
To: {mailTo}
Subject: {subj}
Date: {date}
MIME-Version: 1.0
Content-Type: multipart/mixed; boundary={boundary}

--{boundary}
Content-Type: text/plain; charset="utf-8"

{message_text}

--{boundary}
Content-Type: application/octet-stream
Content-Disposition: attachment; filename="{attachment_path.split('/')[-1]}"
Content-Transfer-Encoding: base64

{attachment_encoded}

--{boundary}--
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


def citeste_configurare(file_path):
    with open(file_path, 'r') as file:
        config = json.load(file)
    return config

config = citeste_configurare('config.json')
mysql_config = config['mysql']
# print(mysql_config)

views = Blueprint('views', __name__)
lista=[]

@views.route('/main', methods=['GET','POST'])
@login_required
def main():
    email = session.get('email')
    user = Users.query.filter_by(username=email).first()
    code = session.get('verified_code')
    cod = session.get('cod')
    if code == cod:
        return render_template('main.html', email = user.username)
    else:
        return render_template('auth.html')
    


@views.route('/verify', methods=['GET', 'POST'])
@login_required
def verify():
    email = session.get('email')
    code = None
    if request.method == 'POST':
        user_code = request.form['code']
        cod = session.get('cod')
        if user_code == cod:
            user = Users.query.filter_by(username=email).first()
            print("AVEM ID USER: ", user)
            login_user(user)
            code = user_code
            session['verified_code'] = code
            return redirect(url_for('views.main', email=email))
        else:
            flash('Cod incorect. Încearcă din nou.')
    return render_template('verify.html')

@views.route('/raport_client', methods=['GET','POST'])
@login_required
def welcome():
    email = session.get('email')
    cod = session.get('cod')
    code = session.get('verified_code')
    if code == cod:
        print("iesi afar")
        if request.method == 'POST':
            print("hai ca merge", request.form.get('excelFileInput'))
            # if 'excelFileInput' in request.files:
            global fisierDeVanzari
            fisierDeVanzari = request.files["excelFileInput"]
            print(fisierDeVanzari,'--------ds--s-d-sd-sdss-s-s--s-ds-d--d-s-d-s-d-s-s--s-d-sd--g--gr-')
            # return fisierDeVanzari
            file_path="C:/Dezvoltare/E-Factura/2023/eFactura/Konica/eFacturaKonicaMinolta local/Baza de date vanzari/"
            # file_path="/home/efactura/efactura_konica/bazaDateVanzari"
            cale_fisier_temp = os.path.join(file_path + '/', 'fisierFacturi.xml' )
            fisierDeVanzari.save(cale_fisier_temp)
            cale_fisier_excel="C:/Dezvoltare/E-Factura/2023/eFactura/Konica/eFacturaKonicaMinolta local/Baza de date vanzari/output.xlsx"
            # fisierDeVanzari.save(file_path+"baza de date.xlsx")
            # fisierDeVanzari=str(file_path+fisierDeVanzari)
            xml_to_excel(cale_fisier_temp, cale_fisier_excel)
            prelucrareDate(cale_fisier_excel)
            session['fisierDeVanzari'] = cale_fisier_excel  
        return render_template('pagina_excel.html')
            
    else:
        return render_template('auth.html')


@views.route('/summary', methods=['GET','POST'])
@login_required
def summary():
    email = session.get('email')
    cod = session.get('cod')
    code = session.get('verified_code')
    if code == cod:
        fisierDeVanzari = session.get('fisierDeVanzari')
        # print("acesta e fisierul de vanzari ", fisierDeVanzari)
     
        # print(fisierDeVanzari,'-----------------------in summary')
        primaFactura, ultimaFactura, totalFactura, numarFacturiTrimise, facturiNuleUnice, numarFacturi = prelucrareDate(fisierDeVanzari)
        numarFacturiCorecte = numarFacturiTrimise - facturiNuleUnice
        print(facturiNuleUnice, "facturi corecte")
        session['ultimaFactura'] = ultimaFactura
        print(type(ultimaFactura))
        # parts = ultimaFactura.split(":")
        # ultimaFactura = parts[1].strip()
        # if type(ultimaFactura) == str :
        #     # Dacă este doar cifre, convertim valoarea la int pentru a fi folosită în JavaScript
        #     numar_ultima_factura_js = int(ultimaFactura)
        # else:
        #     # Dacă nu conține doar cifre, lăsăm valoarea neschimbată
        #     numar_ultima_factura_js = ultimaFactura
            
        # if primaFactura.isdigit():
        #     # Dacă este doar cifre, convertim valoarea la int pentru a fi folosită în JavaScript
        #     primaFactura_js = int(primaFactura)
        # else:
        #     # Dacă nu conține doar cifre, lăsăm valoarea neschimbată
        #     primaFactura_js = primaFactura
        
        print(primaFactura, ultimaFactura, totalFactura, numarFacturiCorecte, numarFacturi)
        return render_template('summary.html', primaFactura=primaFactura, ultimaFactura=ultimaFactura, totalFactura=totalFactura, nrFacturiTrimise=numarFacturiTrimise, numarFacturiCorecte=numarFacturiCorecte, facturiNuleUnice=facturiNuleUnice, numarFacturi = numarFacturi)
    else:
        return render_template('auth.html')

@views.route('/fail', methods=['GET','POST'])
@login_required
def fail():
    email = session.get('email')
    email = session.get('email')
    cod = session.get('cod')
    code = session.get('verified_code')
    if code == cod:
        return render_template('fail.html')
    else:
        return render_template('auth.html')

@views.route('/download_excel', methods=['GET','POST'])
@login_required
def download_excel():
    cod = session.get('cod')
    code = session.get('verified_code')
    if code == cod:
        try:
            excel_file_path = "C:/Dezvoltare/E-Factura/2023/eFactura/Konica/eFacturaKonicaMinolta local/logs/informatii.txt"
            # excel_file_path = "/home/efactura/efactura_konica/logs/informatii.txt"
            return send_file(excel_file_path, as_attachment=True, download_name='Informatii erori facturi.txt')
        except:
            return render_template('auth.html')
    else:
        return render_template('auth.html')
    
# @views.route('/trimitere_anaf', methods=['GET','POST'])
# @login_required
# def trimitere_anaf():
#     # current_datetime = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
#     email = session.get('email')
#     cod = session.get('cod')
#     code = session.get('verified_code')
#     if code == cod:
#         if request.method == 'GET':
#             # filename = 'rezultat '+str(current_datetime)+'.zip'
#             filename = 'rezultatArhiveConversie.zip'
#             eFactura()
#             # listaMesajeEroare2 = listaMesajeEroare
#             # print("mergi fa ", listaMesajeEroare2)
#     else:
#         return render_template('auth.html')
        

#     return send_from_directory('C:/Dezvoltare/E-Factura/2023/eFactura/Konica/eFacturaKonicaMinolta local/output arhive conversie PDF', filename, as_attachment = True)
    # return send_from_directory('/home/efactura/efactura_konica/outputArhiveConversiePDF', filename, as_attachment = True)
@views.route('/trimitere_anaf', methods=['GET','POST'])
@login_required
def trimitere_anaf():
    email = session.get('email')
    cod = session.get('cod')
    code = session.get('verified_code')
    if code == cod:
        if request.method == 'GET':
            filename = 'rezultatArhiveConversie.zip'
            
            def generate():
                # Începem procesul eFactura() într-un fir de execuție separat
                Thread(target=eFactura).start()
                # Returnăm un răspuns preliminar către Azure
                yield "Processing...\n"
                # Așteptăm ca procesul eFactura() să se termine
                eFactura()
                # După ce procesul este complet, facem redirect către ruta de descărcare a arhivei
                yield redirect(url_for('download_arhiva'))
            
            # Returnăm un răspuns cu transferul fragmentat
            return Response(generate(), mimetype='text/plain', headers={'Transfer-Encoding': 'chunked'})
        
        # Dacă cererea este de tip POST
        else:
            # Procesați cererea POST și apoi faceți redirect doar dacă arhiva a fost descărcată în prealabil
            if session.get('arhiva_descarcata'):
                return redirect(url_for('alt_rută'))  # Faceți redirect către altă rută
    
    # Dacă cererea este de tip GET și arhiva a fost descărcată, atunci faceți redirect către altă rută
    elif session.get('arhiva_descarcata'):
        return redirect(url_for('alt_rută'))  # Faceți redirect către altă rută
    
    # Dacă codul nu corespunde sau arhiva nu a fost descărcată, atunci afișați template-ul de autentificare
    else:
        return render_template('auth.html')

@views.route('/download_arhiva', methods=['GET'])
def download_arhiva():
    filename = 'rezultatArhiveConversie.zip'
    return send_from_directory('/home/efactura/efactura_expeditors/outputArhiveConversiePDF', filename, as_attachment=True)
   
@views.route("/statusFacturi", methods=['GET','POST'])
@login_required
def statusFacturi():
    lista.clear()
    email = session.get('email')
    cod = session.get('cod')
    code = session.get('verified_code')
    valoare = request.form.get("download")
    mesaje = interogareTabela() 
    if request.method=='GET':
        idSelectate=request.args.get('iduri_selectate')
        print(request.args)
        print(idSelectate, '-iduri selectate')
        if code == cod:
            session['idSelectate'] = idSelectate
            listaMesajeRulareCurenta = listaFactt
            print(listaMesajeRulareCurenta, " aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
            # asta e aici sa o testam ca primim id-ul tabelei din interfata
            # print(valoare)
            lista.append(idSelectate)
            # lista.clear()
            
        
        descarcarepdf(lista)
        # if request.method=='POST':
        #     trimitereMail()
        return render_template("status spv tabel.html", mesaje=mesaje, listaMesajeRulareCurenta=listaMesajeRulareCurenta)
    else:
        return render_template('auth.html')
    
@views.route("/statusFacturiPrimite", methods=['GET','POST'])
@login_required
def statusFacturiPrimite():
    lista.clear()
    email = session.get('email')
    cod = session.get('cod')
    code = session.get('verified_code')
    valoare = request.form.get("download")
    mesaje = interogareTabelaPrimite() 
    if request.method=='GET':
        idSelectate=request.args.get('iduri_selectate')
        print(request.args)
        print(idSelectate, '-iduri selectate')
        if code == cod:
            session['idSelectate'] = idSelectate
            listaMesajeRulareCurenta = listaFactt
            print(listaMesajeRulareCurenta, " aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
            # asta e aici sa o testam ca primim id-ul tabelei din interfata
            # print(valoare)
            lista.append(idSelectate)
            # lista.clear()
            
        
        descarcarepdfPrimite(lista)
        # if request.method=='POST':
        #     trimitereMail()
        return render_template("status spv tabel primite.html", mesaje=mesaje, listaMesajeRulareCurenta=listaMesajeRulareCurenta)
    else:
        return render_template('auth.html')
@views.route('/download', methods=['GET'])
@login_required
def download_file():
    # Specificați calea către fișierul pe care doriți să îl descărcați
    cod = session.get('cod')
    code = session.get('verified_code')
    idSelectate=request.args.get('iduri_selectate')
    print(request.args)
    print(idSelectate, '-iduri selectate')
    if code == cod:
        session['idSelectate'] = idSelectate
        listaMesajeRulareCurenta = listaFactt
        print(listaMesajeRulareCurenta, " aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
        # asta e aici sa o testam ca primim id-ul tabelei din interfata
        # print(valoare)
        lista.append(idSelectate)
        print(lista,'-------------+++++++++++++++++++++++')
        # lista.clear()
    
    descarcarepdf(lista)
    trimitereMail()
    # Utilizați funcția send_file pentru a trimite fișierul către utilizator
    return render_template("main.html")

@views.route('/downloadPrimite', methods=['GET'])
@login_required
def download_file_recevied():
    # Specificați calea către fișierul pe care doriți să îl descărcați
    cod = session.get('cod')
    code = session.get('verified_code')
    idSelectate=request.args.get('iduri_selectate')
    print(request.args)
    print(idSelectate, '-iduri selectate')
    if code == cod:
        session['idSelectate'] = idSelectate
        listaMesajeRulareCurenta = listaFactt
        print(listaMesajeRulareCurenta, " aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
        # asta e aici sa o testam ca primim id-ul tabelei din interfata
        # print(valoare)
        lista.append(idSelectate)
        print(lista,'-------------+++++++++++++++++++++++')
        # lista.clear()
    
    descarcarepdfPrimite(lista)
    trimitereMail()
    # Utilizați funcția send_file pentru a trimite fișierul către utilizator
    return render_template("main.html")

# @views.route('/downloadPrimite', methods=['GET'])
# @login_required
# def download_file_primite():
#     # Specificați calea către fișierul pe care doriți să îl descărcați
#     cod = session.get('cod')
#     code = session.get('verified_code')
#     idSelectate=request.args.get('iduri_selectate')
#     print(request.args)
#     print(idSelectate, '-iduri selectate')
#     if code == cod:
#         session['idSelectate'] = idSelectate
#         listaMesajeRulareCurenta = listaFactt
#         print(listaMesajeRulareCurenta, " aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
#         # asta e aici sa o testam ca primim id-ul tabelei din interfata
#         # print(valoare)
#         lista.append(idSelectate)
#         print(lista,'-------------+++++++++++++++++++++++')
#         # lista.clear()
#     listaPrimite = interogareFisierePDFPrimite()
#     print("AVEM LISTA PRIMITE ", listaPrimite)    
#     # for i in range(0, len(lista)):
#     #     for j in listaPrimite
    
#     descarcarepdf(lista)
#     # trimitereMail()
#     # Utilizați funcția send_file pentru a trimite fișierul către utilizator
#     return render_template("main.html")

def receive_data():
    data_from_js = request.json.get('variableFromJS')
    print("Data received from JavaScript:", data_from_js)
    # Poți face aici orice dorești cu datele primite
    return jsonify({'message': 'Data received successfully'})

@views.route('/status', methods=['GET','POST'])
@login_required
def status():
    email = session.get('email')
    cod = session.get('cod')
    code = session.get('verified_code')
    if code == cod:
        # primaFactura, ultimaFactura, totalFactura, numarFacturiTrimise = prelucrareDate()
        ultimaFactura = session.get('ultimaFactura')
        resultIstoric = nrFacturiIstoric()
        print(resultIstoric)
        for numar in resultIstoric:
            for numarIstoric in numar:
                print(numarIstoric)
        return render_template('status.html', ultimaFactura = ultimaFactura, totalFactura=numarIstoric)
    else:
        return render_template('auth.html')

@views.route('/generate-new-code', methods=['GET', 'POST'])
@login_required
def generate_new_code():
    email = session.get('email')
    if email:  # Verifică dacă există adresa de email în sesiune
        key = pyotp.random_base32()
        totp = pyotp.TOTP(key)
        new_code = totp.now()
        session['cod'] = new_code
        print(new_code)  # Afișează codul în consola serverului (Python)
        trimitereOTPMail(new_code, email)
        return new_code
    return 'Adresa de email nu este prezentă în sesiune.'


@views.route('/receive_data', methods=['POST'])
@login_required
def receive_data():
    data_from_js = request.json.get('variableFromJS')
    print("Data received from JavaScript:", data_from_js)
    # Poți face aici orice dorești cu datele primite
    return jsonify({'message': 'Data received successfully'})


@views.route('/add_new_clients', methods=["GET", "POST"])
def addClient():
    if request.method == "POST":
        numeClient = request.form.get('numeClient')
        tara = request.form.get('tara')
        cust = request.form.get('cust')
        cui = request.form.get('cui')
        oras = request.form.get('oras')
        strada = request.form.get('strada')
        regiune = request.form.get('judeteDropdown')

    

        connection = pymysql.connect(
            host=mysql_config['host'],
            user=mysql_config['user'],
            password=mysql_config['password'],
            database=mysql_config['database']
        )

        cursor = connection.cursor()

        insert_query = "INSERT INTO clients (name, country, `cust#`, regno, city, street, region) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        values = (numeClient, tara, cust, cui, oras, strada, regiune)
        print(values)
        try:
            cursor.execute(insert_query, values)
            connection.commit()
        except Exception as e:
            connection.rollback()
            print(f"Error: {e}")
        finally:
            cursor.close()
            # connection.close()

    return render_template('addClient.html')
def query_clients_table():
    connection = pymysql.connect(
        host=mysql_config['host'],
        user=mysql_config['user'],
        password=mysql_config['password'],
        database=mysql_config['database']
    )

    cursor = connection.cursor()
    select_query = "SELECT * FROM CLIENTS"
    cursor.execute(select_query)

    results_clients = []
    for row in cursor.fetchall():
        result_dict = {
            "id": row[0],
            "name": row[1],
            "country": row[2],
            "cust": row[3],
            "regno": row[4],
            "city": row[5],
            "street": row[6],
            "region": row[7]
        }
        results_clients.append(result_dict)

    cursor.close()
    # connection.close()

    return results_clients

# Rută pentru vizualizarea clienților
@views.route('/clients', methods=["GET", "POST"])
def view_clients():
    if request.method == "GET":
        mesaj = query_clients_table()
        return render_template('baza_de_date_clienti.html', mesaj=mesaj)

# Rută pentru ștergerea unui client
@views.route('/delete-client', methods=["POST"])
def delete_client():
    client_id = request.form.get('id')
    
    # connection = pymysql.connect(
    #     host="localhost",
    #     user="root",
    #     password="denis",
    #     database="efactura"
    # )
    connection = pymysql.connect(
        host=mysql_config['host'],
        user=mysql_config['user'],
        password=mysql_config['password'],
        database=mysql_config['database']
    )

    cursor = connection.cursor()

    try:
        delete_query = "DELETE FROM clients WHERE id=%s"
        cursor.execute(delete_query, (client_id,))
        connection.commit()
        success = True
        message = "Clientul a fost șters cu succes din baza de date."
    except Exception as e:
        connection.rollback()
        success = False
        message = f"Eroare la ștergerea clientului: {e}"
    finally:
        cursor.close()
        # connection.close()

    return jsonify({'success': success, 'message': message})

@views.route('/save-edited-client', methods=["POST"])
def save_edited_client():
    if request.method == "POST":
        client_id = request.form.get('id')
        numeClient = request.form.get('numeClient')
        tara = request.form.get('tara')
        cust = request.form.get('cust')
        cui = request.form.get('cui')
        oras = request.form.get('oras')
        strada = request.form.get('strada')
        regiune = request.form.get('judeteDropdown')

        print(numeClient,tara)

        # connection = pymysql.connect(
        #     host="localhost",
        #     user="root",
        #     password="denis",
        #     database="efactura"
        # )
        connection = pymysql.connect(
            host=mysql_config['host'],
            user=mysql_config['user'],
            password=mysql_config['password'],
            database=mysql_config['database']
        )

        cursor = connection.cursor()

        update_query = "UPDATE clients SET name=%s, country=%s, `cust#`=%s, regno=%s, city=%s, street=%s, region=%s WHERE id=%s"
        values = (numeClient, tara, cust, cui, oras, strada, regiune, client_id)
        
        try:
            cursor.execute(update_query, values)
            connection.commit()
            success = True
            message = "Clientul a fost actualizat cu succes în baza de date."
        except Exception as e:
            connection.rollback()
            success = False
            message = f"Eroare la actualizarea clientului: {e}"
        finally:
            cursor.close()
            # connection.close()

    return jsonify({'success': success, 'message': message})

@views.route('/refresh', methods=['GET'])
@login_required
# def refresh():
#     def mesajeanafRefresh(headers, val1, val2):
#         time.sleep(15)
#         cif = dateFirma['cui']

#         current_time = datetime.datetime.now()
#         start_time = current_time - datetime.timedelta(days=60)
#         val1 = int(time.mktime(start_time.timetuple())) * 1000

#         X = 0
#         result = datetime.datetime.now() - datetime.timedelta(seconds=X)
#         val2 = int(datetime.datetime.timestamp(result) * 1000)

#         print("val1 ", val1)
#         print("val2 ", val2)

#         apiListaFacturi = f'https://api.anaf.ro/prod/FCTEL/rest/listaMesajePaginatieFactura'

#         params = {
#             'startTime': val1,
#             'endTime': val2,
#             'cif': cif,
#             'pagina': 1
#         }
#         while True:
#             try:
#                 response = requests.get(apiListaFacturi, params=params, headers=headers)

#                 if response.status_code == 200:
#                     data = response.json()
#                     print(data)
#                     if 'eroare' in data:
#                         time.sleep(5)
#                     else:
#                         numar_pagini = data.get('numar_total_pagini')
#                         print(numar_pagini, 'numar pagini')
#                         api_url_updated = f'{apiListaFacturi}?startTime={val1}&endTime={val2}&cif={cif}&pagina={numar_pagini}'

#                         listaMesaje = requests.get(api_url_updated, headers=headers)
#                         raspunsMesajeFacturi = json.loads(listaMesaje.text)
#                         stocareMesajeAnaf(raspunsMesajeFacturi)
#                         print('stocare a mesajelor cu success')
#                         break
#             except:
#                 print(f'Eroare la cererea API, cod de stare: {response.status_code}')
#                 time.sleep(10)

#     print('aici vedem mesajele anaf')
#     headers = {'Authorization': dateFirma['header']}
#     current_time = datetime.datetime.now()
#     start_time = current_time - datetime.timedelta(days=60)
#     val1 = int(time.mktime(start_time.timetuple())) * 1000
#     X = 0
#     result = datetime.datetime.now() - datetime.timedelta(seconds=X)
#     val2 = int(datetime.datetime.timestamp(result) * 1000)

#     mesajeanafRefresh(headers, val1, val2)


def refresh():
    def mesajeanafRefresh(headers, val1, val2):
        time.sleep(5)
        cif = dateFirma['cui']

        current_time = datetime.datetime.now()
        start_time = current_time - datetime.timedelta(days=60)
        val1 = int(time.mktime(start_time.timetuple())) * 1000

        X = 0
        result = datetime.datetime.now() - datetime.timedelta(seconds=X)
        val2 = int(datetime.datetime.timestamp(result) * 1000)

        print("val1 ", val1)
        print("val2 ", val2)

        apiListaFacturi = f'https://api.anaf.ro/prod/FCTEL/rest/listaMesajePaginatieFactura'

        params = {
            'startTime': val1,
            'endTime': val2,
            'cif': cif,
            'pagina': 1
        }
        while True:
            try:
                response = requests.get(apiListaFacturi, params=params, headers=headers)

                if response.status_code == 200:
                    data = response.json()
                    print(data)
                    if 'eroare' in data:
                        print('Eroare în datele primite:', data['eroare'])
                        time.sleep(5)
                    else:
                        numar_pagini = data.get('numar_total_pagini', 1)
                        for pagina in range(1, numar_pagini + 1):
                            params['pagina'] = pagina
                            response = requests.get(apiListaFacturi, params=params, headers=headers)
                            if response.status_code == 200:
                                pagina_data = response.json()
                                print(f'Data pagina {pagina}:', pagina_data)
                                stocareMesajeAnaf(pagina_data)
                            else:
                                print(f'Eroare la cererea API pentru pagina {pagina}, cod de stare: {response.status_code}')
                                break
                        print('Stocare a mesajelor cu succes')
                        break
                else:
                    print(f'Eroare la cererea API, cod de stare: {response.status_code}')
                    time.sleep(5)
            except Exception as e:
                print(f'Eroare la cererea API: {e}')
                time.sleep(5)

    print('Aici vedem mesajele ANAF')
    headers = {'Authorization': dateFirma['header']}
    current_time = datetime.datetime.now()
    start_time = current_time - datetime.timedelta(days=60)
    val1 = int(time.mktime(start_time.timetuple())) * 1000
    X = 0
    result = datetime.datetime.now() - datetime.timedelta(seconds=X)
    val2 = int(datetime.datetime.timestamp(result) * 1000)

    mesajeanafRefresh(headers, val1, val2)

    def stareMesajRefresh():
        listaIdDescarcare.clear()
        for i in range(0, len(listaIndexIncarcare)):
            apiStareMesaj = 'https://api.anaf.ro/prod/FCTEL/rest/stareMesaj?id_incarcare='+str(listaIndexIncarcare[i])
            
            while True:  
                stare = requests.get(apiStareMesaj, headers=headers)
                if stare.status_code == 200:
                    resp = stare.text
                    root = ET.fromstring(resp)
                    staree = str(root.attrib['stare'])
                    if staree != 'in prelucrare':
                        break
                    time.sleep(5)
                else:
                    print('Eroare la interogarea API-ului')
                    break

            try:
                id_descarcare = int(root.attrib['id_descarcare']) 
                listaIdDescarcare.append(id_descarcare)
                print('id descarcare',id_descarcare)   
            except:
                print(resp) 
    print("aici am facut starea mesajului")                 
    stareMesajRefresh()
    print(listaIdDescarcare)

    return redirect(url_for("views.statusFacturi"))

@views.route('/refreshReceived', methods=['GET'])
@login_required
# def refreshReceived():
def sincronizareAPIvsBD():
    result_list = interogareIDprimite()
    # print("result list ", len(result_list), result_list)
    # set_result_list = set(result_list)  # Convertim lista în set pentru căutare eficientă

    time.sleep(10)
    
    current_time = datetime.datetime.now()
    start_time = current_time - datetime.timedelta(days=60)
    val1 = int(time.mktime(start_time.timetuple())) * 1000

    X = 0
    result = datetime.datetime.now() - datetime.timedelta(seconds=X)
    val2 = int(datetime.datetime.timestamp(result) * 1000)

    print("val1 ", val1)
    print("val2 ", val2)

    apiListaFacturi = f'https://api.anaf.ro/prod/FCTEL/rest/listaMesajePaginatieFactura'

    params = {
        'startTime': val1,
        'endTime': val2,
        'cif': cif,
        'pagina': 1
    }

    while True:
        try:
            response = requests.get(apiListaFacturi, params=params, headers=headers)

            if response.status_code == 200:
                data = response.json()
                if 'eroare' in data:
                    time.sleep(5)
                else:
                    numar_pagini = data.get('numar_total_pagini')
                    print(numar_pagini, 'numar pagini')
                    api_url_updated = f'{apiListaFacturi}?startTime={val1}&endTime={val2}&cif={cif}&pagina={numar_pagini}'

                    listaMesaje = requests.get(api_url_updated, headers=headers, timeout=30)
                    if listaMesaje.status_code == 200:
                        raspunsMesajeFacturi = listaMesaje.json()
                        listaIDANAF = [int(mesaj['id']) for mesaj in raspunsMesajeFacturi['mesaje'] if mesaj['tip'] == 'FACTURA PRIMITA']

                        # print("Lista ID-uri ANAF: ", listaIDANAF, "lungimea id anaf ", len(listaIDANAF))

                        # Convertirea ID-urilor în întregi
                        result_list = [int(id) for id in result_list]

                        listaDiferente = [id for id in listaIDANAF if id not in result_list]

                        # print("Lista diferențe: ", listaDiferente, "lungimea diferente ", len(listaDiferente))
                        print("Lista diferențe: ", listaDiferente)
                        # Filtrarea mesajelor pentru a păstra doar cele din listaDiferente
                        
                        listaDiferente = [str(id) for id in listaDiferente]
                        mesajeFiltrate = [mesaj for mesaj in raspunsMesajeFacturi['mesaje'] if mesaj['id'] in listaDiferente]
                        rezultat_final = {'mesaje': mesajeFiltrate}
                        # print(mesajeFiltrate)
                        # Stocare mesaje filtrate
                        print("urmeaza insert")
                        stocareMesajeAnafPrimite(rezultat_final)
                        # print(rezultat_final)
                        print('Stocare a mesajelor cu success')
                        break
                    else:
                        print(f'Eroare la cererea API, cod de stare: {listaMesaje.status_code}')
                        time.sleep(10)
            else:
                time.sleep(10)
        except KeyError as e:
            print(e)
            time.sleep(10)
        except Exception as e:
            print(f'Eroare: {e}')
            time.sleep(10)
            
    def descarcare():
        for i in range(0, len(listaDiferente)):
            apiDescarcare = 'https://api.anaf.ro/prod/FCTEL/rest/descarcare?id='+str(listaDiferente[i])

            descarcare = requests.get(apiDescarcare, headers=headers, timeout=30)

            if descarcare.status_code == 200:
                # print("Cererea a fost efectuata cu succes!")
                with open('C:/Dezvoltare/E-Factura/2023/eFactura/Konica/eFacturaKonicaMinolta local/output zip api/fisier'+str(listaDiferente[i])+'.zip', 'wb') as file:
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
        
    stocarePDFPrimite()
    print('s-au stocat facturile primite')
    # stergeFisiere('C:/Dezvoltare/E-Factura/2023/eFactura/Konica/eFacturaKonicaMinolta local/output conversie', '.zip')
    return redirect(url_for("views.statusFacturiPrimite"))

# print('Aici vedem mesajele ANAF')
# sincronizareAPIvsBD()

# @views.route('/refreshReceived', methods=['GET'])
# @login_required
# def refreshReceived():
#     sincronizareAPIvsBD()
#     def mesajeanafRefresh(headers, val1, val2):
#         time.sleep(15)
#         cif = dateFirma['cui']

#         current_time = datetime.datetime.now()
#         start_time = current_time - datetime.timedelta(days=60)
#         val1 = int(time.mktime(start_time.timetuple())) * 1000

#         X = 0
#         result = datetime.datetime.now() - datetime.timedelta(seconds=X)
#         val2 = int(datetime.datetime.timestamp(result) * 1000)

#         print("val1 ", val1)
#         print("val2 ", val2)

#         apiListaFacturi = f'https://api.anaf.ro/prod/FCTEL/rest/listaMesajePaginatieFactura'

#         params = {
#             'startTime': val1,
#             'endTime': val2,
#             'cif': cif,
#             'pagina': 1
#         }
#         while True:
#             try:
#                 response = requests.get(apiListaFacturi, params=params, headers=headers)

#                 if response.status_code == 200:
#                     data = response.json()
#                     print(data)
#                     if 'eroare' in data:
#                         time.sleep(5)
#                     else:
#                         numar_pagini = data.get('numar_total_pagini')
#                         print(numar_pagini, 'numar pagini')
#                         api_url_updated = f'{apiListaFacturi}?startTime={val1}&endTime={val2}&cif={cif}&pagina={numar_pagini}'

#                         listaMesaje = requests.get(api_url_updated, headers=headers)
#                         raspunsMesajeFacturi = json.loads(listaMesaje.text)
#                         stocareMesajeAnaf(raspunsMesajeFacturi)
#                         print('stocare a mesajelor cu success')
#                         break
#             except:
#                 print(f'Eroare la cererea API, cod de stare: {response.status_code}')
#                 time.sleep(10)

#     print('aici vedem mesajele anaf')
#     headers = {'Authorization': dateFirma['header']}
#     current_time = datetime.datetime.now()
#     start_time = current_time - datetime.timedelta(days=60)
#     val1 = int(time.mktime(start_time.timetuple())) * 1000
#     X = 0
#     result = datetime.datetime.now() - datetime.timedelta(seconds=X)
#     val2 = int(datetime.datetime.timestamp(result) * 1000)

#     mesajeanafRefresh(headers, val1, val2)

#     def stareMesajRefresh():
#         listaIdDescarcare.clear()
#         for i in range(0, len(listaIndexIncarcare)):
#             apiStareMesaj = 'https://api.anaf.ro/prod/FCTEL/rest/stareMesaj?id_incarcare='+str(listaIndexIncarcare[i])
            
#             while True:  
#                 stare = requests.get(apiStareMesaj, headers=headers)
#                 if stare.status_code == 200:
#                     resp = stare.text
#                     root = ET.fromstring(resp)
#                     staree = str(root.attrib['stare'])
#                     if staree != 'in prelucrare':
#                         break
#                     time.sleep(5)
#                 else:
#                     print('Eroare la interogarea API-ului')
#                     break

#             try:
#                 id_descarcare = int(root.attrib['id_descarcare']) 
#                 listaIdDescarcare.append(id_descarcare)
#                 print('id descarcare',id_descarcare)   
#             except:
#                 print(resp) 
#     print("aici am facut starea mesajului")                 
#     stareMesajRefresh()
#     print(listaIdDescarcare)

    # return redirect(url_for("views.statusFacturiPrimite"))

@views.route('/refreshClienti', methods=['GET'])
@login_required
def CUI_process():
    # Conectare la baza de date MySQL
    connection = pymysql.connect(host=mysql_config['host'],
    user=mysql_config['user'],
    password=mysql_config['password'],
    database=mysql_config['database'])

    # Creați un cursor pentru a executa interogările SQL
    cursor = connection.cursor()

    try:
        # Interogați baza de date pentru a obține toate valorile din coloana `regno`
        cursor.execute("SELECT regno, `cust#` FROM clients")
        # Obțineți toate valorile din interogare
        regno_cust_values = cursor.fetchall()

        # Parcurgem fiecare înregistrare din interogare
        for regno, cust in regno_cust_values:
            ccc = []
            dataCautare = datetime.datetime.now().date()
            print(dataCautare)

            if "RO" in regno or "RO " in regno:
                b = str(regno).replace("RO", "").replace(" ","")
                ccc.append(b)
            else:
                ccc.append(regno)

            listaUnicaCui = list(set(ccc))

            for cui in listaUnicaCui:
                cui_without_prefix = cui.replace('RO', '')  # Elimină prefixul "RO" din CUI
                payload = [{'cui': cui_without_prefix, 'data': str(dataCautare)}]
                response = requests.post('https://webservicesp.anaf.ro/PlatitorTvaRest/api/v8/ws/tva', json=payload)
                
                if response.status_code == 200:
                    date_api_complete = response.json()
                    
                    if 'found' in date_api_complete and date_api_complete['found']:
                        for found_item in date_api_complete['found']:
                            clientName = str(found_item["date_generale"]["denumire"])
                            country = 'RO'
                            cui = str(found_item['date_generale']['cui'])
                            city = str(found_item["adresa_domiciliu_fiscal"]["ddenumire_Localitate"])
                            street = str(found_item["adresa_domiciliu_fiscal"]["ddenumire_Strada"]) + " " + str(found_item["adresa_domiciliu_fiscal"]["dnumar_Strada"])
                            regiune = str(found_item["adresa_domiciliu_fiscal"]['dcod_JudetAuto'])
                            
                            # Corectare a variabilei "sector"
                            sector = "SECTOR" + str(found_item["adresa_domiciliu_fiscal"]["dcod_Localitate"])

                            # Actualizăm baza de date cu informațiile obținute din API
                            try:  
                                if 'Sector' in city:
                                    cursor.execute("UPDATE clients SET name = %s, country = %s, city = %s, street = %s, region = %s WHERE regno = %s", 
                                                   (clientName, country, sector, street, regiune, regno))
                                    print(clientName, country, sector, street, regiune, regno)
                                else:
                                    cursor.execute("UPDATE clients SET name = %s, country = %s, city = %s, street = %s, region = %s WHERE regno = %s", 
                                                   (clientName, country, city, street, regiune, regno))
                                    print("aici nu e sector")
                            except Exception as e:
                                print(f'Eroare la actualizarea bazei de date: {e}')
                    else:
                        print(f'Nu s-au găsit informații pentru CUI-ul: {cui_without_prefix}')
                else:
                    print(f'Eroare la solicitarea către API: Cod de stare {response.status_code}')
    except Exception as e:
        print(f'Eroare: {e}')
    finally:
        # Facem commit după ce am terminat operațiile cu baza de date
        connection.commit()
        # Închideți conexiunea la baza de date
        # connection.close()
    return redirect(url_for("views.view_clients"))