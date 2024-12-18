from flask import Blueprint, render_template, redirect, request, session, flash, send_file, send_from_directory, url_for
from flask_login import login_user, login_required, logout_user, current_user
import time
import sqlite3
from flask import jsonify
import pyotp
# import mysql.connector
# import jsonify
# from flask import jsonify
from . import db
from .apeluri_efactura import *
# from .prelucrareDate import *
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
import re
from email.message import EmailMessage
from email.utils import formataddr
from email.mime.base import MIMEBase
from email import encoders
def stergeFisiere(downlXMLbaza, file_extension):
    for root, dirs, files in os.walk(downlXMLbaza):
        for file in files:
            if file.endswith(file_extension):
                os.remove(os.path.join(root, file))

    # Ștergem fișierele din directorul specificat
# stergeFisiere(downlXMLbaza, file_extension)
def send_email(sender_email, receiver_email, password, subject, body, attachment_path):
        msg = EmailMessage()
        msg['From'] = formataddr(('GTRDigital', sender_email))
        msg['To'] = ', '.join(receiver_email)
        msg['CC'] = "invoices-spv@intrarom.ro"
        msg['Subject'] = subject

        msg.set_content(body)

        with open(attachment_path, 'rb') as f:
            file_data = f.read()
            file_name = os.path.basename(attachment_path)

        msg.add_attachment(file_data, maintype='application', subtype='octet-stream', filename=file_name)

        context = ssl.create_default_context()

        # try:
        with smtplib.SMTP("smtp.office365.com", 587) as server:
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            server.login(sender_email, password)
            server.send_message(msg)
            print(f"Email trimis către {receiver_email} cu atașamentul {file_name}.")
        # except Exception as e:
        #     print(f"Eroare la trimiterea e-mailului: {e}")

def trimiteremailseparat(locatie):
    print("====trimiteremail")
    smtp_server = "smtp.office365.com"
    port = 587  # Pentru starttls
    sender_email = "GTRDigital@ro.gt.com"
    password = "g[&vuBR9WQqr=7>D"
    context = ssl.create_default_context()
    message_text = "Hello,\n\nPlease find above the downloaded invoices.\n\nThank you,\nGTRDigital"
    
    date = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    subj = "Facturi SPV " + str(date)
    mailTo = "invoices-spv@intrarom.ro"
    # destinatie = "C:/Users/bogdan.constantinesc/Documents/Intrarom local - Copy/destinatie/"
    # destinatie = '/home/efactura/efactura_intrarom/destinatie/'

    with zipfile.ZipFile(locatie, 'r') as zip_ref:
        zip_ref.extractall("/home/efactura/efactura_intrarom/extracted_files10/")
    folder_path = '/home/efactura/efactura_intrarom/extracted_files10/downloadpdfbazadate'
    folder_path2='/home/efactura/efactura_intrarom/extracted_files10'
    word = 'semnatura'
    for file in os.listdir(folder_path):
        if word in str(file):
            os.remove(folder_path+"/"+str(file))

    for file in os.listdir("/home/efactura/efactura_intrarom/extracted_files10/downloadpdfbazadate"):
        print("----------------")
        # print(file)
        if file.endswith(".xml"):
            print(str(file))
            tree = ET.parse(os.path.join("/home/efactura/efactura_intrarom/extracted_files10/downloadpdfbazadate", file))
            root = tree.getroot()

            namespace = {'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2'}
            sender_email = "GTRDigital@ro.gt.com"
            password = "g[&vuBR9WQqr=7>D"

            
            listacui=['RO462468','RO23245026','RO37561959','RO6120740','RO29146323','RO16461817','RO12276949','RO32254147','RO397270','336290','RO18870966','RO32228016','RO7108590','RO21348475','RO16425725','RO9190626','RO28701573','RO30053945','RO4754740','RO49014769','RO38047949','RO43323242','25717206','RO5919324','RO29193422','RO27787860','RO10148013','RO6003804','RO27846339','RO45496479','RO1590678','26894044','RO9225651','RO27398685','RO19159024','RO27929841','RO18870966','RO10696741','RO20899840','RO14491544','RO13093222','RO31682021','RO17563840','RO15739088','RO26560885','RO14094749','RO2977428','RO13838336','RO37499245','RO1592989','RO752','RO7681112','RO48935803','RO35639040','RO8249644','RO42118983','RO27651515','RO37350714','RO8037897','RO23091725','RO13209247','RO4021138','RO33597275','RO21310535','RO12950179','RO802734','RO25211380','RO8721959','RO18924489','RO17129957','RO29597137','RO36642745','RO37900249','RO22818206','RO9942028','RO10547308','RO27747319','RO4797725','14942091','RO1590082','RO11201891','RO15058256','RO9010105','RO26600548','RO29783938','RO33941343','RO37474798','RO5888716','RO32302597','RO16291216','RO5990324','RO10329729','RO45273051','RO32774506','RO5158762','RO6723660','RO45227063','RO8808380','RO14872336','RO3273781','RO19451400','RO29534899','RO22088675','RO3884955','RO33326284','RO17753151','RO32801198','RO15928982','RO25222010','RO21763919','RO361536','RO14368348','RO16398418','38232539','RO6597308','RO14368143','RO8971726','RO31400589','RO8451308', 'RO462468','RO37561959','RO7108590','RO9942028','RO9010105','RO8971726']
            listaadreseprimite1 = ['dorian.ghenea@INTRAROM.RO', 'kostas.gounaris@INTRAROM.RO', 'dorian.ghenea@INTRAROM.RO', 'human.resources@INTRAROM.RO', 'sorin.cojocaru@INTRAROM.RO', 'kostas.gounaris@INTRAROM.RO', 'bogdan.malureanu@intrarom.ro', 'MagdaM@INTRAROM.RO', 'bogdan.malureanu@intrarom.ro', 'human.resources@INTRAROM.RO', 'bogdan.malureanu@intrarom.ro', 'bogdan.malureanu@intrarom.ro', 'dorian.ghenea@INTRAROM.RO', 'human.resources@INTRAROM.RO', 'MonicaA@INTRAROM.RO', 'MagdaM@INTRAROM.RO', 'MagdaM@INTRAROM.RO', 'kostas.gounaris@INTRAROM.RO', 'gabriela.nae@INTRAROM.RO', 'bogdan.malureanu@intrarom.ro', 'bogdan.malureanu@intrarom.ro', 'AdrianZ@INTRAROM.RO', 'MagdaM@INTRAROM.RO', 'human.resources@INTRAROM.RO', 'bogdan.malureanu@intrarom.ro', 'bogdan.malureanu@intrarom.ro', 'bogdan.malureanu@intrarom.ro', 'sorin.cojocaru@INTRAROM.RO', 'bogdan.malureanu@intrarom.ro', 'gabriela.nae@INTRAROM.RO', 'gabriela.nae@INTRAROM.RO', 'dorian.ghenea@INTRAROM.RO', 'bogdan.malureanu@intrarom.ro', 'bogdan.malureanu@intrarom.ro', 'bogdan.malureanu@intrarom.ro', 'bogdan.malureanu@intrarom.ro', 'bogdan.malureanu@intrarom.ro', 'human.resources@INTRAROM.RO', 'MagdaM@INTRAROM.RO', 'sorin.cojocaru@INTRAROM.RO', 'bogdan.malureanu@intrarom.ro', 'maricel.gherghe@intrarom.ro', '', 'maricel.gherghe@intrarom.ro', 'bogdan.malureanu@intrarom.ro', 'MagdaM@INTRAROM.RO', 'bogdan.malureanu@intrarom.ro', 'sorin.cojocaru@INTRAROM.RO', 'kostas.gounaris@INTRAROM.RO', 'gabriela.nae@INTRAROM.RO', 'bogdan.malureanu@intrarom.ro', 'MagdaM@INTRAROM.RO', 'human.resources@INTRAROM.RO', 'sebastian.andrita@INTRAROM.RO', 'bogdan.malureanu@intrarom.ro', 'AdrianZ@INTRAROM.RO', 'Camelia.batariga@INTRAROM.RO', 'Camelia.batariga@INTRAROM.RO', 'sorin.cojocaru@INTRAROM.RO', 'human.resources@intrarom.ro', 'kostas.gounaris@INTRAROM.RO', 'MonicaA@INTRAROM.RO', 'bogdan.malureanu@intrarom.ro', 'kostas.gounaris@INTRAROM.RO', 'dorian.ghenea@INTRAROM.RO', 'AdrianZ@INTRAROM.RO', 'bogdan.malureanu@intrarom.ro', 'kostas.gounaris@INTRAROM.RO', 'ioana.lefterescu@intrarom.ro', 'kostas.gounaris@INTRAROM.RO', 'MonicaA@INTRAROM.RO', 'MagdaM@INTRAROM.RO', 'kostas.gounaris@INTRAROM.RO', 'human.resources@INTRAROM.RO', 'dorian.ghenea@INTRAROM.RO', 'kostas.gounaris@INTRAROM.RO', 'bogdan.malureanu@intrarom.ro', 'sebastian.andrita@INTRAROM.RO', 'AdrianZ@INTRAROM.RO', 'human.resources@INTRAROM.RO', 'human.resources@INTRAROM.RO', 'MonicaA@INTRAROM.RO', 'human.resources@intrarom.ro', 'sebastian.andrita@INTRAROM.RO', 'victor.dreossi@INTRAROM.RO', 'MagdaM@INTRAROM.RO', 'sebastian.andrita@INTRAROM.RO', 'human.resources@INTRAROM.RO', 'victor.dreossi@INTRAROM.RO', 'gabriela.nae@INTRAROM.RO', 'bogdan.malureanu@intrarom.ro', 'bogdan.malureanu@intrarom.ro', 'MonicaA@INTRAROM.RO', 'MagdaM@INTRAROM.RO', 'bogdan.malureanu@intrarom.ro', 'human.resources@INTRAROM.RO', 'MonicaA@INTRAROM.RO', 'kostas.gounaris@INTRAROM.RO', 'AdrianZ@INTRAROM.RO', 'camelia.batariga@INTRAROM.RO', 'AdrianZ@INTRAROM.RO', 'sebastian.andrita@INTRAROM.RO', 'MagdaB@INTRAROM.RO', 'bogdan.malureanu@intrarom.ro', 'sebastian.andrita@INTRAROM.RO', 'human.resources@INTRAROM.RO', 'AdrianZ@INTRAROM.RO', 'sebastian.andrita@INTRAROM.RO', 'kostas.gounaris@INTRAROM.RO', 'gabriela.nae@INTRAROM.RO', 'human.resources@INTRAROM.RO', 'gabriela.nae@INTRAROM.RO', 'sorin.cojocaru@INTRAROM.RO', 'MonicaA@INTRAROM.RO', 'sorin.cojocaru@INTRAROM.RO', 'sebastian.andrita@INTRAROM.RO', 'dorian.ghenea@INTRAROM.RO', 'human.resources@INTRAROM.RO', 'human.resources@INTRAROM.RO', 'marius.jelescu@INTRAROM.RO', 'luciann@INTRAROM.RO', 'marius.jelescu@INTRAROM.RO', 'luciann@INTRAROM.RO', 'monica.slincu@INTRAROM.RO; marius.jelescu@INTRAROM.RO', 'marius.jelescu@INTRAROM.RO']
            aprobator2=['', '', '', 'AdrianZ@INTRAROM.RO', '', '', 'sebastian.andrita@INTRAROM.RO', 'AdrianZ@INTRAROM.RO', 'sebastian.andrita@INTRAROM.RO', 'AdrianZ@INTRAROM.RO', 'sebastian.andrita@INTRAROM.RO', 'sebastian.andrita@INTRAROM.RO', '', 'AdrianZ@INTRAROM.RO', 'dorian.ghenea@INTRAROM.RO', '', '', '', '', 'sebastian.andrita@INTRAROM.RO', 'sebastian.andrita@INTRAROM.RO', '', '', 'AdrianZ@INTRAROM.RO', 'sebastian.andrita@INTRAROM.RO', 'sebastian.andrita@INTRAROM.RO', 'sebastian.andrita@INTRAROM.RO', '', 'sebastian.andrita@INTRAROM.RO', '', '', '', 'sebastian.andrita@INTRAROM.RO', 'sebastian.andrita@INTRAROM.RO', 'sebastian.andrita@INTRAROM.RO', 'sebastian.andrita@INTRAROM.RO', 'sebastian.andrita@INTRAROM.RO', 'AdrianZ@INTRAROM.RO', '', '', 'sebastian.andrita@INTRAROM.RO', '', '', '', 'sebastian.andrita@INTRAROM.RO', 'AdrianZ@INTRAROM.RO', 'sebastian.andrita@INTRAROM.RO', '', '', '', 'sebastian.andrita@INTRAROM.RO', '', 'AdrianZ@INTRAROM.RO', 'AdrianZ@INTRAROM.RO', 'sebastian.andrita@INTRAROM.RO', '', '', '', '', 'human.resources@intrarom.ro', '', 'dorian.ghenea@INTRAROM.RO', 'sebastian.andrita@INTRAROM.RO', 'kostas.gounaris@INTRAROM.RO', '', '', 'sebastian.andrita@INTRAROM.RO', '', 'dorian.ghenea@INTRAROM.RO', '', 'dorian.ghenea@INTRAROM.RO', '', '', 'AdrianZ@INTRAROM.RO', '', '', 'sebastian.andrita@INTRAROM.RO', 'AdrianZ@INTRAROM.RO', '', 'AdrianZ@INTRAROM.RO', 'AdrianZ@INTRAROM.RO', 'dorian.ghenea@INTRAROM.RO', 'AdrianZ@INTRAROM.RO', 'AdrianZ@INTRAROM.RO', 'dorian.ghenea@INTRAROM.RO', '', 'AdrianZ@INTRAROM.RO', 'AdrianZ@INTRAROM.RO', 'dorian.ghenea@INTRAROM.RO', '', 'sebastian.andrita@INTRAROM.RO', 'sebastian.andrita@INTRAROM.RO', 'dorian.ghenea@INTRAROM.RO', '', 'sebastian.andrita@INTRAROM.RO', 'AdrianZ@INTRAROM.RO', 'dorian.ghenea@INTRAROM.RO', '', '', '', '', 'AdrianZ@INTRAROM.RO', 'AdrianZ@INTRAROM.RO', 'sebastian.andrita@INTRAROM.RO', 'AdrianZ@INTRAROM.RO', 'AdrianZ@INTRAROM.RO', '', 'AdrianZ@INTRAROM.RO', '', '', 'AdrianZ@INTRAROM.RO', '', '', 'dorian.ghenea@INTRAROM.RO', '', 'AdrianZ@INTRAROM.RO', '', 'AdrianZ@INTRAROM.RO', 'AdrianZ@INTRAROM.RO', 'dorian.ghenea@INTRAROM.RO', 'dorian.ghenea@INTRAROM.RO', 'dorian.ghenea@INTRAROM.RO', 'dorian.ghenea@INTRAROM.RO', 'dorian.ghenea@INTRAROM.RO', 'dorian.ghenea@INTRAROM.RO']
            aprobator3=['','','','','','','AdrianZ@INTRAROM.RO','','','','AdrianZ@INTRAROM.RO','AdrianZ@INTRAROM.RO','','','','','','','','AdrianZ@INTRAROM.RO','AdrianZ@INTRAROM.RO','','','','AdrianZ@INTRAROM.RO','AdrianZ@INTRAROM.RO','AdrianZ@INTRAROM.RO','','AdrianZ@INTRAROM.RO','','','','AdrianZ@INTRAROM.RO','AdrianZ@INTRAROM.RO','AdrianZ@INTRAROM.RO','','','','','','AdrianZ@INTRAROM.RO','','','','AdrianZ@INTRAROM.RO','','AdrianZ@INTRAROM.RO','','','','AdrianZ@INTRAROM.RO','','','','AdrianZ@INTRAROM.RO','','','','','AdrianZ@INTRAROM.RO','','','AdrianZ@INTRAROM.RO','','','','','','','','','','','','','','AdrianZ@INTRAROM.RO','','','','','','','','','','','','','','','','','','AdrianZ@INTRAROM.RO','','','','','','','','','','','','','','','','','','','','','','','','', '', '', '', '', '', '']
            
            receiver_email = "cristian.iordache@ro.gt.com"
            message_text = "Hello,\n\nPlease find attached the downloaded invoices.\n\nThank you,\nGTRDigital"

            # Căutarea tag-ului cac:AccountingSupplierParty > Party > PartyTaxScheme > CompanyID
            ns = {
                'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
                'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2'
            }

            # Extrage supplier company id
            supplier_company_id = root.find('.//cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cbc:CompanyID', ns).text

            # Extrage total factura (PayableAmount)
            payable_amount_element = root.find('.//cac:LegalMonetaryTotal/cbc:PayableAmount', ns)
            total_factura = payable_amount_element.text
            currency = root.find('.//cbc:DocumentCurrencyCode', ns).text
            print(supplier_company_id,total_factura,currency)
            adresedeemail=[]
            for k in range(0,len(listacui)):
                print(listacui[k],currency)
                if(str(listacui[k])==str(supplier_company_id)):
                    print("yes")
                    adresedeemail.append(listaadreseprimite1[k])
                    if(str(currency)=="RON"):
                        print("tadam")
                        if(float(total_factura)>500):
                            adresedeemail.append(aprobator2[k])
                        if(float(total_factura)>2500):
                            adresedeemail.append(aprobator3[k])
                    else:
                        print(currency)
                        if(str(currency=="EUR")):
                            print("astfel")
                            if(float(total_factura)>100):
                                adresedeemail.append(aprobator2[k])
                            if(float(total_factura)>500):   
                                adresedeemail.append(aprobator3[k])
            print(supplier_company_id,total_factura,currency)
            date = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
            subject = "Facturi SPV " + date
            if not adresedeemail:
                print("Lista goala")
            else:
                try:
                    send_email(sender_email, adresedeemail, password, subject, message_text,"/home/efactura/efactura_intrarom/extracted_files10/downloadpdfbazadate/" +str(file).replace(".xml",".pdf"))
                except:
                    print("Nu a mers conversia")
    shutil.rmtree(folder_path)
#print()
def trimitereMail(locatie, nume):
    trimiteremailseparat("/home/efactura/efactura_intrarom/destinatie/rezultat.zip")
    smtp_server = "smtp.office365.com"
    port = 587  # Pentru starttls
    sender_email = "GTRDigital@ro.gt.com"
    password = "g[&vuBR9WQqr=7>D"
    context = ssl.create_default_context()
    message_text = "Hello,\n\nPlease find above the downloaded invoices.\n\nThank you,\nGTRDigital"
    
    date = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    subj = "Facturi SPV " + str(date)
    mailTo = "invoices-spv@intrarom.ro" 
    cc_email = "invoices-spv@intrarom.ro"
    # mailTo = "cristian.iordache@ro.gt.com"
    # destinatie = "C:/Dezvoltare/E-Factura/2023/eFactura/Intrarom/Intrarom local - Copy/destinatie/"
    # destinatie = '/home/efactura/efactura_intrarom/destinatie/'
    attachment_path = locatie + nume

    with open(attachment_path, "rb") as attachment:
        attachment_data = attachment.read()
        attachment_encoded = base64.b64encode(attachment_data).decode()

    boundary = "MY_BOUNDARY"

    msg = f"""\
From: {sender_email}
To: {mailTo}
Cc: {cc_email}
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

def stergeFisiere(downlXMLbaza, file_extension):
    for root, dirs, files in os.walk(downlXMLbaza):
        for file in files:
            if file.endswith(file_extension):
                os.remove(os.path.join(root, file))
                
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

@views.route('/raport_client', methods=['GET', 'POST'])
@login_required
def welcome():
    email = session.get('email')
    cod = session.get('cod')
    code = session.get('verified_code')
    stergeFisiere("/home/efactura/efactura_intrarom/outs", '.xml')
    # stergeFisiere('C:/Dezvoltare/E-Factura/2023/eFactura/Intrarom/Intrarom local - Copy/outs', '.xml')
    
    if code == cod:
        if request.method == 'POST':
            files = request.files.getlist('excelFileInput')
            # file_path = "C:/Dezvoltare/E-Factura/2023/eFactura/Intrarom/Intrarom local - Copy/outs"
            file_path = '/home/efactura/efactura_intrarom/outs'
            
            if not files:
                return render_template('pagina_excel.html', files=[])

            processed_files = []

            for file in files:
                cale_fisier_temp = os.path.join(file_path, file.filename)
                file.save(cale_fisier_temp)
                cale_fisier_excel = os.path.join(file_path, 'output_' + file.filename.replace('.xml', '.xlsx'))
                processed_files.append(cale_fisier_excel)
            print(processed_files)
            
            session['fisierDeVanzari'] = processed_files
            return render_template('pagina_excel.html', files=processed_files)
        else:
            return render_template('pagina_excel.html', files=[])
    else:
        return render_template('auth.html')


@views.route('/summary', methods=['GET','POST'])
@login_required
def summary():
    email = session.get('email')
    cod = session.get('cod')
    code = session.get('verified_code')
    
    if code == cod:
        # file_path = "C:/Dezvoltare/E-Factura/2023/eFactura/Intrarom/Intrarom local - Copy/outs"
        file_path = '/home/efactura/efactura_intrarom/outs'
        
        # Verificăm dacă folderul există
        if not os.path.exists(file_path):
            print(f"Folderul {file_path} nu există sau nu poate fi accesat.")
            return render_template('summary.html', primaFactura=None, ultimaFactura=None, totalFactura=0, nrFacturiTrimise=0, numarFacturiCorecte=0, facturiNuleUnice=0, numarFacturi=0)


        ids_facturi = []
        totalFacturaTaxInclusive = 0.0
        
        for file_name in os.listdir(file_path):
            if file_name.endswith('.xml'):
                try:
                    file_full_path = os.path.join(file_path, file_name)
                    tree = ET.parse(file_full_path)
                    root = tree.getroot()
                    namespaces = {
                        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
                        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2'
                    }
                    invoice_id = root.find('.//cbc:ID', namespaces).text
                    ids_facturi.append(invoice_id)
                    
                    # Calculăm suma TaxInclusiveAmount pentru fiecare factură
                    tax_inclusive_amount = root.find('.//cac:LegalMonetaryTotal/cbc:TaxInclusiveAmount', namespaces).text
                    totalFacturaTaxInclusive += float(tax_inclusive_amount)
                    
                except Exception as e:
                    print(f"Eroare la parsarea fișierului {file_full_path}: {str(e)}")
        
        if not ids_facturi:
            return render_template('summary.html', primaFactura=None, ultimaFactura=None, totalFactura=0, nrFacturiTrimise=0, numarFacturiCorecte=0, facturiNuleUnice=0, numarFacturi=0, totalFacturaTaxInclusive=0)
        
        ids_facturi.sort()
        primaFactura = ids_facturi[0]
        ultimaFactura = ids_facturi[-1]
        numarFacturi = len(ids_facturi)
        
        # The following variables need to be calculated or obtained
        totalFactura = 0  # Replace with actual calculation if available
        numarFacturiTrimise = numarFacturi  # Assuming all processed invoices are sent
        facturiNuleUnice = 0  # Replace with actual calculation if available
        numarFacturiCorecte = numarFacturiTrimise - facturiNuleUnice
        
        return render_template('summary.html', 
                               primaFactura=primaFactura, 
                               ultimaFactura=ultimaFactura, 
                               totalFactura=totalFacturaTaxInclusive, 
                               nrFacturiTrimise=numarFacturiTrimise, 
                               numarFacturiCorecte=numarFacturiCorecte, 
                               facturiNuleUnice=facturiNuleUnice, 
                               numarFacturi=numarFacturi)
    
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
            # excel_file_path = "C:/Dezvoltare/E-Factura/2023/eFactura/Intrarom/Intrarom local - Copy/logs/informatii.txt"
            excel_file_path = "/home/efactura/efactura_intrarom/logs/informatii.txt"
            return send_file(excel_file_path, as_attachment=True, download_name='Informatii erori facturi.txt')
        except:
            return render_template('auth.html')
    else:
        return render_template('auth.html')
    
@views.route('/trimitere_anaf', methods=['GET','POST'])
@login_required
def trimitere_anaf():
    # current_datetime = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    email = session.get('email')
    cod = session.get('cod')
    code = session.get('verified_code')
    if code == cod:
        if request.method == 'GET':
            print("aici a intrat pe get")
            # filename = 'rezultat '+str(current_datetime)+'.zip'
            # filename = 'facturiTransmise.txt'
            #try:
            print("ajunge aici")
            eFactura()  
                # trimitere_anaf()
            #    return render_template('main.html')
            listaMesajeEroare2 = listaMesajeEroare
            print("mergi fa ", listaMesajeEroare2)
    else:
        return render_template('auth.html')
        

    # return send_from_directory('C:/Dezvoltare/E-Factura/2023/eFactura/Intrarom/Intrarom local - Copy/Baza de date vanzari', 'facturiTransmise.txt', as_attachment = True)
    return send_from_directory('/home/efactura/efactura_intrarom/bazadatevanzari', 'facturiTransmise.txt', as_attachment = True)

def stareMesaj():
        listaIdDescarcare.clear()
        for i in range(0, len(listaIndexIncarcare)):
            apiStareMesaj = 'https://api.anaf.ro/prod/FCTEL/rest/stareMesaj?id_incarcare='+str(listaIndexIncarcare[i])
            
            while True:  # buclă infinită
                stare = requests.get(apiStareMesaj, headers=headers, timeout=30)
                if stare.status_code == 200:
                    resp = stare.text
                    root = ET.fromstring(resp)
                    staree = str(root.attrib['stare'])
                    # statusStareMesajBD(staree)
            print(listaIndexIncarcare, staree)
               
@views.route("/statusFacturi", methods=['GET','POST'])
@login_required
def statusFacturi():
    
    lista.clear()
    email = session.get('email')
    cod = session.get('cod')
    code = session.get('verified_code')
    valoare = request.form.get("download")
    # -----------------------------------------------------------------------------------------------------------------------------
    
    
    # ---------------------------------------------------------------------------------------------------------------------------------                
    # mesaje = interogareTabela() 
    if request.method=='GET':
        # stergeFisiere('C:/Dezvoltare/E-Factura/2023/eFactura/Intrarom/Intrarom local - Copy/output conversie/', '.xml')
        # stergeFisiere('C:/Dezvoltare/E-Factura/2023/eFactura/Intrarom/Intrarom local - Copy/download pdf baza de date/', '.xml')
        stergeFisiere("/home/efactura/efactura_intrarom/outputConversie", '.xml')
        stergeFisiere("/home/efactura/efactura_intrarom/downloadpdfbazadate", '.xml')
        idSelectate=request.args.get('iduri_selectate')
        print(request.args)
        print(idSelectate, '-iduri selectate')
        if code == cod:
            statusStareMesajBD()
            mesaje = interogareTabelaFacturiTrimise()
            session['idSelectate'] = idSelectate
            listaMesajeRulareCurenta = listaFactt
    #         print(listaMesajeRulareCurenta, " aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
    #         # asta e aici sa o testam ca primim id-ul tabelei din interfata
    #         # print(valoare)
            lista.append(idSelectate)
            lista.clear()
            
        descarcarepdf(lista)
        if request.method=='POST':
            # trimitereMail("C:/Dezvoltare/E-Factura/2023/eFactura/Intrarom/Intrarom local - Copy/destinatie/", "rezultat.zip")
            trimitereMail("/home/efactura/efactura_intrarom/destinatie/", "rezultat.zip")
        # return render_template("status spv tabel.html", mesaje=mesaje, listaMesajeRulareCurenta=listaMesajeRulareCurenta)
    return render_template("status spv tabel.html", mesaje = mesaje, listaMesajeRulareCurenta=listaMesajeRulareCurenta)
    # else:
    #     return render_template('auth.html')
    
@views.route("/statusFacturiPrimite", methods=['GET','POST'])
@login_required
def statusFacturiPrimite():
    stergeFisiere('/home/efactura/efactura_intrarom/downloadPDFBazaDate', '.xml')
    stergeFisiere('/home/efactura/efactura_intrarom/downloadPDFBazaDate', 'pdf')
    stergeFisiere('/home/efactura/efactura_intrarom/outputconversie', '.xml')
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
    
@views.route('/downloadANAF', methods=['GET'])
@login_required
def download_file_ANAF():
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
        lista.append(idSelectate)
        print(lista,'-------------+++++++++++++++++++++++')
    
    # descarcarepdf(lista)
    # trimitereMail()
    # try:
        raspunsANAF(lista)
        stocareZIPAnaf()
        # trimitereMail('C:/Dezvoltare/E-Factura/2023/eFactura/Intrarom/Intrarom local - Copy/output arhive conversie PDF/', 'rezultatArhiveConversie.zip')
        # return render_template("main.html")
    # except:
        # return render_template("status spv tabel.html")
    # return render_template("main.html")
    # filename = 'rezultatArhiveConversie.zip'
    # trimitereMail()
    # return send_from_directory('C:/Dezvoltare/E-Factura/2023/eFactura/Intrarom/Intrarom local - Copy/output arhive conversie PDF', filename, as_attachment = True)
    # return send_from_directory('/home/efactura/efactura_intrarom/outputarhiveconversiepdf', filename, as_attachment = True)
    return redirect(url_for("views.statusFacturi"))

@views.route('/download_invoices', methods=['GET'])
@login_required
def download_file_invoices():
    # Specificați calea către fișierul pe care doriți să îl descărcați
    
    cod = session.get('cod')
    code = session.get('verified_code')
    idSelectatePDF=request.args.get('iduri_selectate2')
    print(request.args)
    print(idSelectatePDF, '-iduri selectate pdf')
    if code == cod:
        session['idSelectate'] = idSelectatePDF
        listaMesajeRulareCurenta = listaFactt
        print(listaMesajeRulareCurenta, " aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
        # asta e aici sa o testam ca primim id-ul tabelei din interfata
        # print(valoare)
        lista.append(idSelectatePDF)
        print(lista,'-------------+++++++++++++++++++++++')
        # lista.clear()
    
    descarcarepdf(lista)
    # trimitereMail("C:/Dezvoltare/E-Factura/2023/eFactura/Intrarom/Intrarom local - Copy/destinatie/", "rezultat.zip")
    trimitereMail("/home/efactura/efactura_intrarom/destinatie/", "rezultat.zip")
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
    # trimitereMail("C:/Dezvoltare/E-Factura/2023/eFactura/Intrarom/Intrarom local - Copy/destinatie/", "rezultat.zip")
    trimitereMail("/home/efactura/efactura_intrarom/destinatie/", "rezultat.zip")
    # Utilizați funcția send_file pentru a trimite fișierul către utilizator
    return render_template("main.html")



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


# -------------------------------------------------------------------------------   ADAUGARE CLIENTI NOI  ----------------------------------------------------------------------------



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


# ------------------------------------------------------------------------------   AFISARE CLIENTI   -----------------------------------------------------------------------

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



# ---------------------------------------------------------------------------- REFRESH FACTURI PRIMITE ------------------------------------------------------------------------------


@views.route('/refreshReceived', methods=['GET'])
@login_required
def sincronizareAPIvsBD():
    listaFinalDiferente = []
    result_list = interogareIDprimite()
    time.sleep(10)

    current_time = datetime.datetime.now()
    start_time = current_time - datetime.timedelta(days=60)
    val1 = int(time.mktime(start_time.timetuple())) * 1000

    X = 5
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

    response = requests.get(apiListaFacturi, params=params, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        if 'eroare' in data:
            time.sleep(5)
        else:
            numar_pagini = data.get('numar_total_pagini')
            listaIDANAF = []
            
            for k in range(1, numar_pagini + 1):
                print(numar_pagini, 'numar pagini')
                api_url_updated = f'{apiListaFacturi}?startTime={val1}&endTime={val2}&cif={cif}&pagina={k}&filtru=P'

                listaMesaje = requests.get(api_url_updated, headers=headers, timeout=30)
                if listaMesaje.status_code == 200:
                    raspunsMesajeFacturi = listaMesaje.json()
                    print(raspunsMesajeFacturi)
                    listaIDANAF.extend(
                        [int(mesaj['id']) for mesaj in raspunsMesajeFacturi['mesaje'] if mesaj['tip'] == 'FACTURA PRIMITA']
                    )
                else:
                    print(f'Eroare la cererea API, cod de stare: {listaMesaje.status_code}')

                result_list = [int(id) for id in result_list]

                listaDiferente = [id for id in listaIDANAF if id not in result_list]

                print("Lista diferențe: ", listaDiferente, "lungimea diferente ", len(listaDiferente))

                listaDiferente = [str(id) for id in listaDiferente]
                print(listaDiferente, 'aici avem ceva cu str')
                mesajeFiltrate = [mesaj for mesaj in raspunsMesajeFacturi['mesaje'] if mesaj['id'] in listaDiferente]
                print(mesajeFiltrate, 'aici filtram')
                rezultat_final = {'mesaje': mesajeFiltrate}
                print(rezultat_final)
                stocareMesajeAnafPrimite(rezultat_final)
            
                def descarcare():
                    for i in range(0, len(listaDiferente)):
                        apiDescarcare = 'https://api.anaf.ro/prod/FCTEL/rest/descarcare?id=' + str(listaDiferente[i])
                        print(apiDescarcare, 'ASTA E API DESCARCARE')

                        descarcare = requests.get(apiDescarcare, headers=headers, timeout=30)

                        if descarcare.status_code == 200:
                            # with open('C:/Dezvoltare/E-Factura/2023/eFactura/Intrarom/Intrarom local - Copy/output zip api/fisier' + str(listaDiferente[i]) + '.zip', 'wb') as file:
                           with open('/home/efactura/efactura_intrarom/outputzipapi/fisier' + str(listaDiferente[i]) + '.zip', 'wb') as file:
                                file.write(descarcare.content)
                                print('Descarcat cu success')
                        else:
                            print("Eroare la efectuarea cererii HTTP:", descarcare.status_code)
                            print(descarcare.text)

                print("aici descarcam folosind id_descarcare")
                descarcare()

        # directory_path = 'C:/Dezvoltare/E-Factura/2023/eFactura/Intrarom/Intrarom local - Copy/output zip api'
        directory_path = '/home/efactura/efactura_intrarom/outputzipapi'

        # output_directory = 'C:/Dezvoltare/E-Factura/2023/eFactura/Intrarom/Intrarom local - Copy/output conversie'
        output_directory = '/home/efactura/efactura_intrarom/outputconversie'

        os.makedirs(output_directory, exist_ok=True)

        for filename in os.listdir(directory_path):
            if filename.endswith('.zip'):
                zip_file_path = os.path.join(directory_path, filename)
                try:
                    with zipfile.ZipFile(zip_file_path, 'r') as zip_file:
                        file_id = filename.replace('fisier', '').replace('.zip', '')
                        for xml_file in zip_file.namelist():
                            if xml_file.endswith('.xml'):
                                with zip_file.open(xml_file) as file:
                                    xml_data = file.read()
                                    # Replace any numeric part in the xml_file name with file_id
                                    new_filename = re.sub(r'\d+', file_id, xml_file)
                                    output_path = os.path.join(output_directory, new_filename)
                                    with open(output_path, 'wb') as output_file:
                                        output_file.write(xml_data)
                except zipfile.BadZipFile:
                    print(f'Fișierul {zip_file_path} nu este un fișier ZIP valid sau este corupt')





    def make_archive(source, destination):
        base = os.path.basename(destination)
        name = base.split('.')[0]
        format = base.split('.')[1]
        archive_from = os.path.dirname(source)
        archive_to = os.path.basename(source.strip(os.sep))
        shutil.make_archive(name, format, archive_from, archive_to)
        shutil.move('%s.%s' % (name, format), destination)   
        
    stocarePDFPrimite()
    print('s-au stocat facturile primite')
    return redirect(url_for("views.statusFacturiPrimite"))

# -----------------------------------------------------------------------    REFRESH CLIENTI   ----------------------------------------------------------------------------

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