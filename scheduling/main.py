from flask import Flask, request, jsonify
from datetime import datetime
import secrets
import string
import logging
from datetime import datetime, date, time
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from models import db, Client, Hairdresser, Service, Appointment, Notification, ApiKeys
from email_config import user, app_password, host, port


# Parámetros iniciales y creación de modelo
app = Flask("api_scheduling")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///scheduling.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Creacion de base de datos
with app.app_context():
	db.create_all()

# Creación de log de la API
logging.basicConfig(filename='scheduling.log', level=logging.DEBUG)

def send_mail(destination, date, time):
	"""Función para el envio de correo"""
	
	try:
		# Configuración del servidor SMTP
		smtp_host = host
		smtp_port = port
		smtp_user = user
		smtp_app_password = app_password

		# Configuración del mensaje
		subject = 'Agendamiento de cita'
		body = 'Cordial saludo,\nEste es un correo de confirmación para su cita en la peluqueria para el día ' + str(date) + 'a las ' + str(time) + '.\nMuchas gracias por la atención prestada.\n\nNo responder a este correo.'

		# Dirección de origen y destinatario
		from_address = user
		to_address = destination

		# Configurar el mensaje MIME
		message = MIMEMultipart()
		message['From'] = from_address
		message['To'] = to_address
		message['Subject'] = subject

		# Agregar el cuerpo del mensaje
		message.attach(MIMEText(body, 'plain'))

		# Iniciar la conexión con el servidor SMTP
		with smtplib.SMTP(smtp_host, smtp_port) as server:
			# Iniciar la conexión segura (STARTTLS)
			server.starttls()

			# Iniciar sesión en el servidor SMTP con la contraseña específica de la aplicación
			server.login(smtp_user, smtp_app_password)

			# Enviar el mensaje
			server.sendmail(from_address, to_address, message.as_string())

		return "Email send successfully."

	except Exception as e:
		return "Error"

@app.route('/generate_apikey', methods=['GET'])
def generate_apikey():
	"""Función para generación de apikeys"""

	try:
		user = request.args.get('user')

		# Validación de que no vengan valores vacíos
		if len(str(user)) == 0:
			logging.error('Error consult parameters, please validate arguments')
			return jsonify({'status': 201, 'messaje':'Error consult parameters, please validate arguments'})
		try:
			
			# Consulta existencia de usuario
			user_validate = ApiKeys.query.filter(ApiKeys.user == user, ApiKeys.state == True).order_by(ApiKeys.id.desc()).first()

			# Si existe retorna la api key, si no existe crea y retorna la nueva apikey
			if user_validate != None:
				if user_validate.state:
					logging.info('User exists, return apikey')
					return jsonify({'status': 200, 'apikey':user_validate.apikey, 'message':'User exists'})

			# Creación de Api Key con la función token_urlsafe
			api_key = ''.join(secrets.choice(string.ascii_letters + string.digits) for i in range(20))
			try:
				# Creación del usuario
				user = ApiKeys(apikey=api_key, user=user)
				db.session.add(user)
				db.session.commit()
				logging.info('User create successfull, return apikey')
				return jsonify({'status': 200, 'apikey':api_key, 'message':'User create successfull'})
					
			except Exception as e:
				logging.error('Error to create user, please consult with administrator '+str(e))
				return jsonify({'status': 202, 'message':'Error to create user, please consult with administrator'})	

		except Exception as e:
			logging.error('Error generate API key, please consult with administrator '+str(e))
			return jsonify({'status': 203, 'messaje':'Error generate API key, please consult with administrator'})

	except Exception as e:
		logging.error('Error consult parameters, please validate arguments '+str(e))
		return jsonify({'status': 201, 'messaje':'Error consult parameters, please validate arguments'})

@app.route('/create_user', methods=['POST'])
def create_user():
	"""Función de peticion para la creacion de usuarios"""

	try:
		# Extracción de datos del json de petición
		name = request.get_json()['name']
		phone = request.get_json()['phone']
		email = request.get_json()['email']
		type_user = request.get_json()['type_user']
		services_user = request.get_json()['services_user']
		
		# Validación de que no vengan valores vacíos
		if len(str(name)) == 0 or len(str(phone)) == 0 or len(str(email)) == 0 or len(str(type_user)) == 0:
			logging.error('Error consult parameters, please validate arguments ')
			return jsonify({'status': 201, 'message':'Error consult parameters, please validate arguments'})

		if type_user not in ['Client','hairdresser']:
			logging.error('Not type available')
			return jsonify({'status': 210, 'message':'Not type available'}) 

		if type_user == 'hairdresser':
			if len(str(services_user)) == 0:
				logging.error('Error consult parameters, please validate arguments ')
				return jsonify({'status': 201, 'message':'Error consult parameters, please validate arguments'})
		# Extracción de apikey desde el Header
		apikey = request.headers.get('apikey')

		try:
			# Consulta de apikey
			api_validation = ApiKeys.query.filter(ApiKeys.apikey == apikey, ApiKeys.state == True).first()

			# Validación de estado de la apikey
			if api_validation != None:

				try:
					# Validación de existencia del usuario
					if type_user == 'Client':
						user_validation = Client.query.filter(Client.email == email).first()
					else:
						user_validation = Hairdresser.query.filter(Hairdresser.name == name).first()

					if user_validation != None:
						logging.info('User exists')
						return jsonify({'status': 208, 'message':'User exists'})
					else:
						try:
							# Creación de usuario
							if type_user == 'Client':
								user = Client(name=name, phone=phone, email=email)
								db.session.add(user)
								db.session.commit()
							else:
								user = Hairdresser(name=name)
								db.session.add(user)

								# Asignacion de productos al usuario
								error_service = []
								for service in services_user:
									service_obj = Service.query.get(service)
									if service_obj != None:
										user.services.append(service_obj)
									else:
										error_service.append(service)

								# Validación de inexistencia de servicios
								if len(error_service) != 0:
									db.session.remove()
									logging.info('Error create user, services not exists'+str(error_service))
									return jsonify({'status': 211, 'message':'Error create user, services not exists'+str(error_service)})

							db.session.commit()
							logging.info('User create successfull')
							return jsonify({'status': 200, 'message':'User create successfull'})

						except Exception as e:
							logging.error('Error create user, please consult with administrator '+str(e))
							return jsonify({'status': 207, 'message':'Error create user, please consult with administrator'})

				except Exception as e:
					logging.error('Error validate user, please consult with administrator '+str(e))
					return jsonify({'status': 206, 'message':'Error validate user, please consult with administrator'})
			else:
				logging.error('API not enabled, please verify your API key')
				return jsonify({'status': 205, 'message':'API not enabled, please verify your API key'})

		except Exception as e:
			logging.error('Error validate API key, please consult with administrator '+str(e))
			return jsonify({'status': 204, 'message':'Error validate API key, please consult with administrator'})

	except Exception as e:
		logging.error('Error consult parameters, please validate arguments '+str(e))
		return jsonify({'status': 201, 'message':'Error consult parameters, please validate arguments'})

@app.route('/get_users', methods=['GET'])
def get_users():
	"""Función de petición para consultar todos los usuarios de un típo"""
	try:
		# Extracción de datos del json de petición
		type_user = request.args.get('type_user')

		if type_user not in ['Client','hairdresser']:
			logging.error('Not type available')
			return jsonify({'status': 210, 'message':'Not type available'}) 
		# Extraccion de apikey desde el Header
		apikey = request.headers.get('apikey')

		try:
			# Consulta de apikey
			api_validation = ApiKeys.query.filter(ApiKeys.apikey == apikey, 
				ApiKeys.state == True).first()

			# Validación de estado de la apikey
			if api_validation != None:

				# Consulta de todos los usuarios
				if type_user == 'Client':
					users = Client.query.all()
				else:
					users = Hairdresser.query.all()

				if users != None:
					# Estructuración de usuarios para retorno
					if type_user == 'Client':
						result = {
							'Clients': [
								{'id': user.id, 
								'name': user.name, 
								'phone': user.phone, 
								'email': user.email}
								for user in users
							]
						}
					else:
						result = {
							'Hairdresser': [
								{'id': user.id, 
								'name': user.name, 
								'services': [{'id': service.id, 
								'name': service.name} for service in user.services]}
								for user in users
							]
						}

					logging.info('Result users: '+str(result))
					return jsonify({'status': 200, 'message':'Consult successfull', 'data':result})
				else:
					logging.error('Not users register')
					return jsonify({'status': 209, 'message':'Not users register'})

			else:
				logging.error('API not enabled, please verify your API key')
				return jsonify({'status': 205, 'message':'API not enabled, please verify your API key'})

		except Exception as e:
			logging.error('Error validate API key, please consult with administrator '+str(e))
			return jsonify({'status': 204, 'message':'Error validate API key, please consult with administrator'})

	except Exception as e:
		logging.error('Error consult parameters, please validate arguments '+str(e))
		return jsonify({'status': 201, 'message':'Error consult parameters, please validate arguments'})

@app.route('/create_service', methods=['POST'])
def create_service():
	"""Funcion de petición para la creación de servicios"""

	try:
		# Extracción de datos del json de petición
		service = request.get_json()['service']
		
		# Validación de que no vengan valores vacíos
		if len(str(service)) == 0:
			logging.error('Error consult parameters, please validate arguments ')
			return jsonify({'status': 201, 'message':'Error consult parameters, please validate arguments'})

		# Extracción de apikey desde el Header
		apikey = request.headers.get('apikey')

		try:
			# Consulta de apikey
			api_validation = ApiKeys.query.filter(ApiKeys.apikey == apikey, 
				ApiKeys.state == True).first()

			# Validación de estado de la apikey
			if api_validation != None:

				try:
					# Validación de existencia del servicio
					service_validation = Service.query.filter(Service.name == service.upper()).first()

					if service_validation != None:
						logging.info('Service exists')
						return jsonify({'status': 212, 'message':'Service exists'})
					else:
						try:
							# Creación de servicio
							service_obj = Service(name=service.upper())
							db.session.add(service_obj)
							db.session.commit()

							logging.info('Service create successfull')
							return jsonify({'status': 200, 'message':'Service create successfull'})

						except Exception as e:
							logging.error('Error create service, please consult with administrator '+str(e))
							return jsonify({'status': 213, 'message':'Error create service, please consult with administrator'})

				except Exception as e:
					logging.error('Error validate service, please consult with administrator '+str(e))
					return jsonify({'status': 214, 'message':'Error validate service, please consult with administrator'})
			else:
				logging.error('API not enabled, please verify your API key')
				return jsonify({'status': 205, 'message':'API not enabled, please verify your API key'})

		except Exception as e:
			logging.error('Error validate API key, please consult with administrator '+str(e))
			return jsonify({'status': 204, 'message':'Error validate API key, please consult with administrator'})

	except Exception as e:
		logging.error('Error consult parameters, please validate arguments '+str(e))
		return jsonify({'status': 201, 'message':'Error consult parameters, please validate arguments'})

@app.route('/get_services', methods=['GET'])
def get_services():
	"""Función de petición para consultar todos los servicios"""
		
	# Extraccion de apikey desde el Header
	apikey = request.headers.get('apikey')

	try:
		# Consulta de apikey
		api_validation = ApiKeys.query.filter(ApiKeys.apikey == apikey, 
			ApiKeys.state == True).first()

		# Validación de estado de la apikey
		if api_validation != None:

			# Consulta de todos los servicios
			services = Service.query.all()

			if services != None:
				# Estructuración de servicios para retorno
				result = {
					'Services': [
						{'id': service.id, 
						'name': service.name}
						for service in services
					]
				}

				logging.info('Result services: '+str(result))
				return jsonify({'status': 200, 'message':'Consult successfull', 'data':result})
			else:
				logging.error('Not services register')
				return jsonify({'status': 209, 'message':'Not services register'})

		else:
			logging.error('API not enabled, please verify your API key')
			return jsonify({'status': 205, 'message':'API not enabled, please verify your API key'})

	except Exception as e:
		logging.error('Error validate API key, please consult with administrator '+str(e))
		return jsonify({'status': 204, 'message':'Error validate API key, please consult with administrator'})

@app.route('/book_appointment', methods=['POST'])
def book_appointment():
	"""Funcion de petición para la creación de servicios"""

	try:
		# Extracción de datos del json de petición
		date = request.get_json()['date']
		time = request.get_json()['time']
		client_id = request.get_json()['client_id']
		hairdresser_id = request.get_json()['hairdresser_id']
		service_id = request.get_json()['service_id']
		
		# Validación de que no vengan valores vacíos
		if len(str(date)) == 0 or len(str(time)) == 0 or len(str(client_id)) == 0 or len(str(hairdresser_id)) == 0 or len(str(service_id)) == 0:
			logging.error('Error consult parameters, please validate arguments ')
			return jsonify({'status': 201, 'message':'Error consult parameters, please validate arguments'})

		# Extracción de apikey desde el Header
		apikey = request.headers.get('apikey')

		try:
			# Consulta de apikey
			api_validation = ApiKeys.query.filter(ApiKeys.apikey == apikey, 
				ApiKeys.state == True).first()

			# Validación de estado de la apikey
			if api_validation != None:

				try:
					# Validación de existencia del cliente
					client_validation = Client.query.get(client_id)

					if client_validation:
						try:
							# Validación de existencia del peluquero
							hairdresser_validation = Hairdresser.query.get(hairdresser_id)

							if hairdresser_validation:
								try:
									# Validación de existencia del servicio
									service_validation = Service.query.get(service_id)

									if service_validation:

										# Validación de existencia del servicio para el peluquero
										if service_validation in hairdresser_validation.services:

											try:
												# Validación de existencia de unca cita para el peluquero en el mismo horario
												appointment_validation = Appointment.query.filter(Appointment.hairdresser_id == hairdresser_id, Appointment.date == datetime.strptime(date,"%Y-%m-%d").date(),
													Appointment.time == datetime.strptime(time,"%H:%M:%S").time(), Appointment.state==False).first()

												# Si no existe una cita para ese horario se creara una
												if appointment_validation == None:
													appointment_obj = Appointment(date=datetime.strptime(date,"%Y-%m-%d").date(), 
														time=datetime.strptime(time,"%H:%M:%S").time(), 
														client_id=client_validation.id,
														hairdresser_id=hairdresser_validation.id, 
														service_id=service_validation.id)
													db.session.add(appointment_obj)
													db.session.commit()

													resp = send_mail(Client.email,date, time)

													if resp != 'Error':
														logging.info('Appointment scheduled successfully')
														return jsonify({'status': 200, 'message':'Appointment scheduled successfully'})
													else:
														logging.info('Appointment scheduled successfully but confirmation email no send.')
														return jsonify({'status': 224, 'message':'Appointment scheduled successfully but confirmation email no send.'})
												else:
													logging.error('Error create appointment, busy hairdresser schedule')
													return jsonify({'status': 215, 'message':'Error create appointment, busy hairdresser schedule'})

											except Exception as e:
												logging.error('Error create appointment, please consult with administrator '+str(e))
												return jsonify({'status': 216, 'message':'Error create appointment, please consult with administrator'})

										else:
											logging.error('Error validation service, service not exists for hairdresser')
											return jsonify({'status': 217, 'message':'Error validation service, service not exists for hairdresser'})
									else:
										logging.error('Error validation service, service not exists')
										return jsonify({'status': 218, 'message':'Error validation service, service not exists'})

								except Exception as e:
									logging.error('Error validation service, please consult with administrator '+str(e))
									return jsonify({'status': 219, 'message':'Error validation service, please consult with administrator'})
							else:
								logging.error('Error validation hairdresser, hairdresser not exist')
								return jsonify({'status': 220, 'message':'Error validation hairdresser, hairdresser not exist'})
						except Exception as e:
							logging.error('Error validation hairdresser, please consult with administrator '+str(e))
							return jsonify({'status': 221, 'message':'Error validation hairdresser, please consult with administrator'})
					else:
						logging.error('Error validation client, client not exists')
						return jsonify({'status': 222, 'message':'Error validation client, client not exists'})

				except Exception as e:
					logging.error('Error validate client, please consult with administrator '+str(e))
					return jsonify({'status': 223, 'message':'Error validate client, please consult with administrator'})
			else:
				logging.error('API not enabled, please verify your API key')
				return jsonify({'status': 205, 'message':'API not enabled, please verify your API key'})

		except Exception as e:
			logging.error('Error validate API key, please consult with administrator '+str(e))
			return jsonify({'status': 204, 'message':'Error validate API key, please consult with administrator'})

	except Exception as e:
		logging.error('Error consult parameters, please validate arguments '+str(e))
		return jsonify({'status': 201, 'message':'Error consult parameters, please validate arguments'})

@app.route('/best_client', methods=['GET'])
def best_client():

	# Extraccion de apikey desde el Header
	apikey = request.headers.get('apikey')

	try:
		# Consulta de apikey
		api_validation = ApiKeys.query.filter(ApiKeys.apikey == apikey, 
			ApiKeys.state == True).first()

		# Validación de estado de la apikey
		if api_validation != None:

			try:
				# Consulta del usuario que más solicitudes ha realizado
				client = Appointment.query.with_entities(Appointment.client_id, db.func.count(Appointment.client_id).label('total')).group_by(Appointment.client_id).order_by(db.desc('total')).first()
				user = Client.query.get(client[0])
				result = {
					'id': user.id, 
					'name': user.name, 
					'phone': user.phone, 
					'email': user.email,
					'number_petition': client[1]
				}
				
				return jsonify({'status': 200, 'message':'The best client', 'data':result})
			except Exception as e:
				logging.error('Error consulting best client, please consult with administrator '+str(e))
				return jsonify({'status': 225, 'message':'Error consulting best client, please consult with administrator'})
		else:
			logging.error('API not enabled, please verify your API key')
			return jsonify({'status': 205, 'message':'API not enabled, please verify your API key'})

	except Exception as e:
		logging.error('Error validate API key, please consult with administrator '+str(e))
		return jsonify({'status': 204, 'message':'Error validate API key, please consult with administrator'})

@app.route('/best_service', methods=['GET'])
def best_service():
	# Extraccion de apikey desde el Header
	apikey = request.headers.get('apikey')

	try:
		# Consulta de apikey
		api_validation = ApiKeys.query.filter(ApiKeys.apikey == apikey, 
			ApiKeys.state == True).first()

		# Validación de estado de la apikey
		if api_validation != None:

			try:
				# Consulta del servicio que más han solicitudes
				service = Appointment.query.with_entities(Appointment.service_id, db.func.count(Appointment.service_id).label('total')).group_by(Appointment.service_id).order_by(db.desc('total')).first()
				servi = Service.query.get(service[0])
				result = {
					'id': servi.id, 
					'name': servi.name,
					'number_petition': service[1]
				}
				
				return jsonify({'status': 200, 'message':'More frequent service', 'data':result})
			except Exception as e:
				logging.error('Error consulting best service, please consult with administrator '+str(e))
				return jsonify({'status': 226, 'message':'Error consulting best service, please consult with administrator'})
		else:
			logging.error('API not enabled, please verify your API key')
			return jsonify({'status': 205, 'message':'API not enabled, please verify your API key'})

	except Exception as e:
		logging.error('Error validate API key, please consult with administrator '+str(e))
		return jsonify({'status': 204, 'message':'Error validate API key, please consult with administrator'})

@app.route('/predict_twodays', methods=['GET'])
def predict_twodays():
	# Extraccion de apikey desde el Header
	apikey = request.headers.get('apikey')

	try:
		# Consulta de apikey
		api_validation = ApiKeys.query.filter(ApiKeys.apikey == apikey, 
			ApiKeys.state == True).first()

		# Validación de estado de la apikey
		if api_validation != None:

			try:
				# Consulta de las fechas de todas las citas solicitadas
				dates = Appointment.query.with_entities(Appointment.date, db.func.count(Appointment.date).label('total')).group_by(Appointment.date).order_by(db.desc('total')).all()
				
				# Conversión de los datos en un data frame
				df = pd.DataFrame(dates, columns=['date', 'total'])
				df = df.set_index('date')

				# Creación del modelo ARIMA para uso de series de tiempo y predicción de 2 dias adelante
				model = ARIMA(df, order=(12,1,1)).fit()
				
				result = {
					'one_day_ahead': int(model.forecast(steps=2).values[0]), 
					'two_days_ahead': int(model.forecast(steps=2).values[1])
				}

				return jsonify({'status': 200, 'message':'Customer number prediction', 'data':result})
			except Exception as e:
				logging.error('Error prediction model, please consult with administrator '+str(e))
				return jsonify({'status': 227, 'message':'Error prediction model, please consult with administrator'})
		else:
			logging.error('API not enabled, please verify your API key')
			return jsonify({'status': 205, 'message':'API not enabled, please verify your API key'})

	except Exception as e:
		logging.error('Error validate API key, please consult with administrator '+str(e))
		return jsonify({'status': 204, 'message':'Error validate API key, please consult with administrator'})

if __name__ == '__main__':
	app.run(host="0.0.0.0",debug=True)