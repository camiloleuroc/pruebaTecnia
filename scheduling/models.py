from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date, time

db = SQLAlchemy()

hairdresser_service = db.Table('hairdresser_service',
    db.Column('hairdresser_id', db.Integer, db.ForeignKey('hairdresser.id'), primary_key=True),
    db.Column('service_id', db.Integer, db.ForeignKey('service.id'), primary_key=True)
)

class Client(db.Model):
	"""Clase de creacion de modelo para Clientes"""

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(50), nullable=False)
	phone = db.Column(db.Integer, nullable=False)
	email = db.Column(db.String(120), nullable=False, unique=True)
	date_register = db.Column(db.DateTime, nullable=False, default=datetime.now())


class Hairdresser(db.Model):
	"""Clase de creacion de modelo para Peluqueros"""

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(50), nullable=False)
	date_register = db.Column(db.DateTime, nullable=False, default=datetime.now())
	state = db.Column(db.Boolean, default=True)
	services = db.relationship('Service', secondary=hairdresser_service, backref=db.backref('hairdresser', lazy='dynamic'))


class Service(db.Model):
	"""Clase de creacion de modelo para Servicios"""

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(50), nullable=False)


class Appointment(db.Model):
	"""Clase de creacion de modelo para Agendamiento de Citas"""

	id = db.Column(db.Integer, primary_key=True)
	date = db.Column(db.Date, nullable=False)
	time = db.Column(db.Time, nullable=False)
	state = db.Column(db.Boolean, default=False)
	client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
	hairdresser_id = db.Column(db.Integer, db.ForeignKey('hairdresser.id'), nullable=False)
	service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)


class Notification(db.Model):
	"""Clase de creacion de modelo para Agendamiento de Citas"""

	id = db.Column(db.Integer, primary_key=True)
	subject = db.Column(db.String(100), nullable=False)
	body = db.Column(db.Text, nullable=False)
	client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
	date_register = db.Column(db.DateTime, nullable=False, default=datetime.now())

class ApiKeys(db.Model):
	"""Clase de creacion de modelo para alojar las ApiKeys"""

	id = db.Column(db.Integer, primary_key=True)
	apikey = db.Column(db.String(20), nullable=False, unique=True)
	user = db.Column(db.String(20), nullable=False)
	state = db.Column(db.Boolean, default=True)