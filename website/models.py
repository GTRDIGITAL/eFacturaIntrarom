from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class TrimitereFacturi(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    factura = db.Column(db.Integer)
    index_incarcare = db.Column(db.BigInteger, unique=True, index=True)
    data_trimis = db.Column(db.TIMESTAMP, server_default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))


class StatusMesaje(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data_creare = db.Column(db.BigInteger)
    cif = db.Column(db.String(255))
    id_solicitare = db.Column(db.String(255))
    detalii = db.Column(db.String(500))
    tip = db.Column(db.String(255))
    id_factura = db.Column(db.BigInteger, db.ForeignKey('trimitere_facturi.index_incarcare'))


class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(1000), nullable=False)
    token = db.Column(db.String(100), nullable=False)
    trimiterefact = db.relationship('TrimitereFacturi')


class FisierePDF(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nume_fisier = db.Column(db.String(255))
    continut = db.Column(db.BLOB)
    status_mesaj_id = db.Column(db.String(255), db.ForeignKey('status_mesaje.id_solicitare'))
    status_mesaj = db.relationship('StatusMesaje', backref='fisiere_pdf')


class UltimeleFacturiTrimise(db.Model):
    id_factura = db.Column(db.Integer, primary_key=True)
    numar_factura = db.Column(db.String(255), nullable=False)
    data_trimis = db.Column(db.TIMESTAMP, server_default=func.now())


class TabelaFisierePDF(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nume_fisier = db.Column(db.String(255))
    continut = db.Column(db.BLOB)
