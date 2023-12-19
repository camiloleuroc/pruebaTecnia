import json
import pandas as pd
import re
import pytest
import sys
import os
import subprocess

# Definición de ruta sobre la cual va a actuar pytest
current_directory = os.getcwd()
print(current_directory)
sys.path.append(current_directory+'\\scheduling\\')

# Importación de la app flask
from scheduling.main import app

# Declaración de variable apikey donde se almacenara la apikey con la que interactuarán las otras pruebas
apikey = ""

# Creación del cliente para uso de pytest con flask
@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_generate_apikey(client):
    """Función para pruebas de generación de apikeys"""
    global apikey

    # Declaración del diccionario de pruebas en un dataframe
    users = pd.DataFrame({
        'user':['Camilo', 'Andres', 'Maria', 'Camilo', 'Estefania', '','Paola', 'Pedro', ''],
        'pattern': [r"'apikey': '[a-zA-Z0-9]+'",r"'apikey': '[a-zA-Z0-9]+'",r"'apikey': '[a-zA-Z0-9]+'",r"'apikey': '[a-zA-Z0-9]+'",r"'apikey': '[a-zA-Z0-9]+'","",r"'apikey': '[a-zA-Z0-9]+'",r"'apikey': '[a-zA-Z0-9]+'",""],
        'status': [200,200,200,200,200,201,200,200,201]
    })

    # Ciclo para iterar cada una de las pruebas
    for ind, row in users.iterrows():
        response = client.get('/generate_apikey?user='+str(row['user']))
        if "apikey" in response.get_json().keys():
            apikey = response.get_json()["apikey"]

        if row['pattern'] != "":
            print(str(response.get_json()))
            match = re.search(row['pattern'],str(response.get_json()))
            assert match is not None
        assert response.get_json()["status"] == row['status']
        assert response.status_code == 200

def test_create_services(client):
    """Función para pruebas de creación de servicios"""
    global apikey

    # Declaración del diccionario de pruebas en un dataframe
    users = pd.DataFrame({
        'service':['', 'Corte de cabello', 'Alisado', 'Manicure', 'Corte de cabello'],
        'message': ['Error consult parameters, please validate arguments', 'Service create successfull', 'Service create successfull', 'Service create successfull', 'Service exists'],
        'status': [201, 200, 200, 200, 212]
    })

    headers = {
        "apikey": apikey
    }

    # Ciclo para iterar cada una de las pruebas
    for ind, row in users.iterrows():
        data = {
            "service":row["service"]
        }
        response = client.post('/create_service', json=data, headers=headers)
        assert response.get_json()["status"] == row['status']
        assert response.get_json()["message"] == row['message']
        assert response.status_code == 200

def test_create_user(client):
    """Función para pruebas de creación de usuarios"""
    global apikey

    # Declaración del diccionario de pruebas en un dataframe
    users = pd.DataFrame({
        'name':['', 'Camilo', 'Camilo', 'Camilo', 'Andres', 'Andres'],
        'phone':[32123154, 32123154, 32123154, 32123154, 0, 0],
        'email':['camilo@test.com', 'camilo@test.com', 'camilo@test.com', 'camilo@test.com', 'andres@test.com', 'andres@test.com'],
        'type_user':['', 'Cliente', 'Client', 'Client', 'hairdresser', 'hairdresser'],
        'services_user':[[], [], [], [], [2, 3, 4], [1, 2]],
        'message': ['Error consult parameters, please validate arguments', 'Not type available', 'User create successfull', 'User exists', 'Error create user, services not exists', 'User create successfull'],
        'status': [201, 210, 200, 208, 211, 200]
    })

    headers = {
        "apikey": apikey
    }

    # Ciclo para iterar cada una de las pruebas
    for ind, row in users.iterrows():
        data = {
            "name":row["name"],
            "phone":row["phone"],
            "email":row["email"],
            "type_user":row["type_user"],
            "services_user":row["services_user"]
        }
        response = client.post('/create_user', json=data, headers=headers)
        assert response.get_json()["status"] == row['status']
        assert row['message'] in response.get_json()["message"]
        assert response.status_code == 200

def test_get_users(client):
    """Función para pruebas de consulta de usuarios"""
    global apikey

    # Declaración del diccionario de pruebas en un dataframe
    users = pd.DataFrame({
        'type_user':['', 'Cliente', 'Client', 'hairdresser'],
        'message': ['Not type available', 'Not type available', 'Consult successfull', 'Consult successfull'],
        'status': [210, 210, 200, 200]
    })

    headers = {
        "apikey": apikey
    }

    # Ciclo para iterar cada una de las pruebas
    for ind, row in users.iterrows():
        response = client.get('/get_users?type_user='+row["type_user"], headers=headers)
        assert response.get_json()["status"] == row['status']
        assert response.get_json()["message"] == row['message']
        assert response.status_code == 200

def test_get_services(client):
    """Función para pruebas de consulta de servicios"""
    global apikey

    headers = {
        "apikey": apikey
    }

    # Ciclo para iterar cada una de las pruebas
    response = client.get('/get_services', headers=headers)
    assert response.get_json()["status"] == 200
    assert response.get_json()["message"] == 'Consult successfull'
    assert response.status_code == 200

def test_book_appointment(client):
    """Función para pruebas de agendamiento de citas"""
    global apikey

    # Declaración del diccionario de pruebas en un dataframe
    users = pd.DataFrame({
        'date':['', '2023-12-10', '2023-12-10', '2023-12-10', '2023-12-10', '2023-12-10', '2023-12-10', '2023-12-10', '2023-12-10'],
        'time':['', '12:30:20', '12:30:20', '12:30:20', '12:30:20', '12:30:20', '12:30:20', '12:30:20', '12:30:20'],
        'client_id':['', 8, 1, 1, 1, 1, 1, 1, 1],
        'hairdresser_id':['', 1, 8, 1, 1, 2, 2, 1, 1],
        'service_id':['', 1, 1, 8, 8, 3, 1, 1, 2],
        'message': ['Error consult parameters, please validate arguments', 'Error validation client, client not exists', 'Error validation hairdresser, hairdresser not exist', 'Error validation service, service not exists', 'Error validation service, service not exists', 'Error validation hairdresser, hairdresser not exist', 'Error validation hairdresser, hairdresser not exist', 'Appointment scheduled successfully but confirmation email no send.', 'Error create appointment, busy hairdresser schedule'],
        'status': [201, 222, 220, 218, 218, 220, 220, 224, 215]
    })

    headers = {
        "apikey": apikey
    }

    # Ciclo para iterar cada una de las pruebas
    for ind, row in users.iterrows():
        data = {
            "date":row["date"],
            "time":row["time"],
            "client_id":row["client_id"],
            "hairdresser_id":row["hairdresser_id"],
            "service_id":row["service_id"]
        }
        response = client.post('/book_appointment', json=data, headers=headers)
        assert response.get_json()["status"] == row['status']
        assert row['message'] in response.get_json()["message"]
        assert response.status_code == 200