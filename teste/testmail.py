import yagmail

# Inițializează un obiect Yagmail
yag = yagmail.SMTP('GTRDigital@ro.gt.com', 'g[&vuBR9WQqr=7>D')

# Trimite email
contents = [
    'This is the body of the email.',
    '/path/to/attachment.pdf'  # Adaugă atașamente (opțional)
]

yag.send('cristian.iordache@ro.gt.com', 'Subject of the email', contents)

# Închide conexiunea
yag.close()
