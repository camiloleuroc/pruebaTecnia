# API PARA ADMINISTRACIÓN DE CÍTAS DE PELUQERÍA

Esta API proporciona endpoints para gestionar el agendamiento de citas en una peluquería, crear clientes, peluqueros y servicios.

## Requisitos

- Python 3.8.18
- Flask
- SQLAlchemy
- Pandas
- statsmodels
- pytest

## Instalación (todo se realiza por terminal)

1. Clona este repositorio:

   ```bash
   git clone https://github.com/camiloleuroc/pruebaTecnica.git

2. Crea un environment, a continuación un ejemplo de como crearlo con anaconda3.
   
   ```bash
   conda create -n nombreenv python=3.8.18

3. Se activa el environment.
   
   ```bash
   conda activate nombreenv
   
4. Instalar dependencias

   ```bash
   pip install -r requirements.txt
   
5. Una vez realizado esto dentro del directorio "pruebaTecnica" se ejecutara pytest sin argumento y el solo buscará los archivos test para comprobar el estado del aplicativo.
   
   ```bash
   pytest

6. Ya comprobado se realiza la ejecución dentro del directorio "scheduling"
   
   ```bash
   python main.py

# ENDPOINTS

Según donde se lance el script se debe agregar la url con el puerto 5000 para realizar las peticiones, en este caso que es localhost se utiliza "http://127.0.0.1:5000/":

## peticiones GET

### generate_apikey

Retorna un API KEY para el uso de los demas endpoints

- URL: http://127.0.0.1:5000/generate_apikey
- Example petition curl (<name_user> es un nombre de usuario para asignarle la apikey este debe de ser único):
  ```bash
  curl --location 'http://127.0.0.1:5000/generate_apikey?user=<name_user>'

- response:
  ```bash
  {
    "apikey": "6ApfdXlaIr7A0h4vc3YV",
    "message": "User create successfull",
    "status": 200
   }
- status
  * 200 Correct Response.
  * 201 Error consult parameter user, please validate arguments.
  * 202 Error to create user, please consult with administrator.
  * 203 Error generate API key, please consult with administrator.
    
### get_users

Retorna todos los usuarios registrados

- URL: http://127.0.0.1:5000/get_users
- Example petition curl (<type_user> es el tipo de usuarios que se quieren consultar puede ser 'Client' o 'hairdresser'):
  ```bash
  curl --location 'http://127.0.0.1:5000/get_users?type_user=Client' --header 'apikey: 6ApfdXlaIr7A0h4vc3YV'

- response:
  ```bash
  {
    "data": {
        "Clients": [
            {
                "email": "camilo@test.com",
                "id": 1,
                "name": "Camilo",
                "phone": 3233358
            },
            {
                "email": "andres@test.com",
                "id": 2,
                "name": "Andres",
                "phone": 3233359
            }
        ]
    },
    "message": "Consult successfull",
    "status": 200
   }
- status
  * 200 Correct Response.
  * 201 Error consult parameter user, please validate arguments.
  * 204 Error validate API key, please consult with administrator.
  * 205 API not enabled, please verify your API key.
  * 209 Not users register.
  * 210 Not type available.

### get_services

Retorna todos los servicios registrados

- URL: http://127.0.0.1:5000/get_services
- Example petition curl
   ```bash
   curl --location 'http://127.0.0.1:5000/get_services' --header 'apikey: 6ApfdXlaIr7A0h4vc3YV'
- response:
  ```bash
  {
    "data": {
        "Services": [
            {
                "id": 1,
                "name": "CORTE CABELLO"
            },
            {
                "id": 2,
                "name": "MANICURE"
            },
            {
                "id": 3,
                "name": "PEDICURE"
            }
        ]
    },
    "message": "Consult successfull",
    "status": 200
   }
- status
  * 200 Correct Response.
  * 204 Error validate API key, please consult with administrator.
  * 205 API not enabled, please verify your API key.
  * 209 Not users register.
    
### best_client

Retorna el mejor cliente quien es el que mas citas haya agendado

- URL:http://127.0.0.1:5000/best_client
- Example petition curl
  ```bash
  curl --location 'http://127.0.0.1:5000/best_client' --header 'apikey: 6ApfdXlaIr7A0h4vc3YV'
- response:
  ```bash
  {
    "data": {
        "email": "camilo@test.com",
        "id": 1,
        "name": "Camilo",
        "number_petition": 2,
        "phone": 3023359
    },
    "message": "The best client",
    "status": 200
   }
- status
  * 200 Correct Response.
  * 204 Error validate API key, please consult with administrator.
  * 205 API not enabled, please verify your API key.
  * 225 Error consulting best client, please consult with administrator.
    
### best_service

Retorna el mejor servicio tomando el que mas han solicitado

- URL: http://127.0.0.1:5000/best_service
- Example petition curl
  ```bash
  curl --location 'http://127.0.0.1:5000/best_service' --header 'apikey: 6ApfdXlaIr7A0h4vc3YV'
- response:
  ```bash
  {
    "data": {
        "id": 2,
        "name": "MANICURE",
        "number_petition": 3
    },
    "message": "More frequent service",
    "status": 200
   }
- status
  * 200 Correct Response.
  * 204 Error validate API key, please consult with administrator.
  * 205 API not enabled, please verify your API key.
  * 226 Error consulting best service, please consult with administrator.
    
### predict_twodays

Retorna la una predicción de la cantidad de usuarios que posiblemente pueden venir los 2 dias siguientes (se requieren buena cantidad de datos para ser mas precíso)

- URL: http://127.0.0.1:5000/predict_twodays
- Example petition curl
  ```bash
  curl --location 'http://127.0.0.1:5000/predict_twodays' --header 'apikey: 6ApfdXlaIr7A0h4vc3YV'
- response:
  ```bash
  {
    "data": {
        "one_day_ahead": 4,
        "two_days_ahead": 3
    },
    "message": "Customer number prediction",
    "status": 200
   }
- status
  * 200 Correct Response.
  * 204 Error validate API key, please consult with administrator.
  * 205 API not enabled, please verify your API key.
  * 227 Error prediction model, please consult with administrator.
    
### get_appointments

Agenda una cita y envía un correo de confirmación de la misma

- URL: http://127.0.0.1:5000/get_appointments
- Example petition curl
  ```bash
  curl --location 'http://127.0.0.1:5000/get_appointments' --header 'apikey: 6ApfdXlaIr7A0h4vc3YV'
- response:
  ```bash
  {
    "data": {
        "Appointments": [
            {
                "client_id": 1,
                "date": "2023-06-06",
                "hairdresser_id": 1,
                "id": 1,
                "service_id": 2,
                "time": "10:50:30"
            },
            {
                "client_id": 2,
                "date": "2023-06-06",
                "hairdresser_id": 1,
                "id": 2,
                "service_id": 2,
                "time": "10:50:40"
            }
        ]
    },
    "message": "Appoinments",
    "status": 200
   }
- status
  * 200 Correct Response.
  * 204 Error validate API key, please consult with administrator.
  * 205 API not enabled, please verify your API key.
  * 228 Error consulting appointments, please consult with administrator.
  
## peticiones POST

### create_user

Crea un cliente o un peluquero según el tipo de usuario que se envíe; si se envia el tipo de usuario "Client" crea un cliente si se envía el tipo de usuario "hairdresser" se crea un peluquero.

- URL: http://127.0.0.1:5000/create_user
- Example petition curl Client
  ```bash
  curl --location 'http://127.0.0.1:5000/create_user' \
   --header 'apikey: 6ApfdXlaIr7A0h4vc3YV' \
   --header 'Content-Type: application/json' \
   --data-raw '{
       "name":"Pedro",
       "phone":"3023359",
       "email":"Pedro@test.com",
       "type_user":"Client",
       "services_user":[]
   }'
- response Client:
  ```bash
  {
    "message": "User create successfull",
    "status": 200
   }
- Example petition curl hairdresser (services_user son los ids de los servicios que brindará el peluquero)
  ```bash
  curl --location 'http://127.0.0.1:5000/create_user' \
   --header 'apikey: 6ApfdXlaIr7A0h4vc3YV' \
   --header 'Content-Type: application/json' \
   --data-raw '{
       "name":"Pedro",
       "phone":"0",
       "email":"0",
       "type_user":"hairdresser",
       "services_user":[2,3]
   }'
- response hairdresser:
  ```bash
  {
    "message": "User create successfull",
    "status": 200
   }
- status
  * 200 Correct Response.
  * 201 Error consult parameter user, please validate arguments.
  * 204 Error validate API key, please consult with administrator.
  * 205 API not enabled, please verify your API key.
  * 206 Error validate client, please consult with administrator.
  * 207 Error create client, please consult with administrator.
  * 208 User exists.
  * 210 Not type available.
  * 211 Error create user, services not exists.
    
### create_service

Crea un servicio para poderse asignar a un peluquero en su creación

- URL: http://127.0.0.1:5000/create_service
- Example petition curl (service es el nombre del servicio que se va a brindar)
  ```bash
  curl --location 'http://127.0.0.1:5000/create_service' \
   --header 'apikey: 6ApfdXlaIr7A0h4vc3YV' \
   --header 'Content-Type: application/json' \
   --data '{
       "service":"pedicure"
   }'
- response:
  ```bash
  {
    "message": "Service create successfull",
    "status": 200
   }
- status
  * 200 Correct Response.
  * 201 Error consult parameter user, please validate arguments.
  * 204 Error validate API key, please consult with administrator.
  * 205 API not enabled, please verify your API key.
  * 212 Service exists.
  * 213 Error create service, please consult with administrator.
  * 214 Error validate service, please consult with administrator.
    
### book_appointment

Agenda una cita y envía un correo de confirmación de la misma

- URL: http://127.0.0.1:5000/book_appointment
- Example petition curl (el campo date debe estar en formato YYYY-MM-DD, el campo time HH:MM:SS, los ids son los ids del cliente, peluquero y servicio que se va a solicitar)
  ```bash
  curl --location 'http://127.0.0.1:5000/book_appointment' \
   --header 'apikey: 6ApfdXlaIr7A0h4vc3YV' \
   --header 'Content-Type: application/json' \
   --data '{
       "date":"2023-06-08",
       "time":"10:50:00",
       "client_id":"1",
       "hairdresser_id":"1",
       "service_id":"3"
   }'
- response:
  ```bash
  {
    "message": "Appointment scheduled successfully.",
    "status": 200
   }
- status
  * 200 Correct Response.
  * 201 Error consult parameter user, please validate arguments.
  * 204 Error validate API key, please consult with administrator.
  * 205 API not enabled, please verify your API key.
  * 215 Error create appointment, busy hairdresser schedule.
  * 216 Error create appointment, please consult with administrator.
  * 217 Error validation service, service not exists for hairdresser.
  * 218 Error validation service, service not exists.
  * 219 Error validation service, please consult with administrator.
  * 220 Error validation service, hairdresser not exist.
  * 221 Error validation hairdresser, please consult with administrator.
  * 222 Error validation client, client not exists.
  * 223 Error validate client, please consult with administrator.
  * 224 Appointment scheduled successfully but confirmation email no send.
    
### update_appointment

Agenda una cita y envía un correo de confirmación de la misma

- URL: http://127.0.0.1:5000/update_appointment
- Example petition curl (appointment es el id de la cita que se quiere actualizar y marcar como completada)
  ```bash
  curl --location 'http://127.0.0.1:5000/update_appointment' \
   --header 'apikey: 6ApfdXlaIr7A0h4vc3YV' \
   --header 'Content-Type: application/json' \
   --data '{
       "appointment":"1"
   }'
- response:
  ```bash
  {
    "message": "Update appointment successfully",
    "status": 200
   }
- status
  * 204 Error validate API key, please consult with administrator.
  * 205 API not enabled, please verify your API key.
  * 229 Error update appointments, please consult with administrator.
