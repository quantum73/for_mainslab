import random
from typing import TypedDict, List, Dict, Optional, Union

import pandas as pd
from django.core.files.uploadedfile import InMemoryUploadedFile


class ServiceClassificator(TypedDict):
    """
    Класс, представляющих тип возвращаемых данных классификатора услуг

    Атрибуты
    ---------
    service_class: int
        класс сервиса
    service_name: str
        имя сервиса
    """
    service_class: int
    service_name: str


class ClientsAndOrganizations(TypedDict):
    """
    Класс, представляющих тип возвращаемых данных о клиентах и организациях

    Атрибуты
    ---------
    clients_data: list
        список имён клиентов
    organizations_data: dict
        словарь данных клиентских организаций
    """
    clients_data: List
    organizations_data: Dict


def fraud_detector(service: Optional[str] = None) -> float:
    # TODO:
    #  Непонятно зачем принимать на вход str и прогонять колонку service,
    #  если функция должна лишь выдавать рандомное значение в диапазоне от 0 до 1?
    """
    Возвращает случайное значение в диапазоне от 0 до 1

    Параметры
    ---------
    service: str, optional
        описание сервиса

    Возвращаемое значение
    ---------------------
    float
        случайное значение в диапазоне от 0 до 1
    """
    return random.random()


def service_classificator(service: Optional[str] = None) -> ServiceClassificator:
    # TODO:
    #  Аналогичная ситуация.
    #  Зачем принимать на вход str и прогонять колонку service,
    #  если функция должна лишь выдавать рандомную пару из словаря service_types
    """
    Возвращает случайную пару ключ-значение из словаря service_types

    Параметры
    ---------
    service: str, optional
        описание сервиса (опционально)

    Возвращаемое значение
    ---------------------
    dict
        словарь с ключами service_class и service_name
    """
    service_types = {
        1: "консультация",
        2: "лечение",
        3: "стационар",
        4: "диагностика",
        5: "лаборатория",
    }
    random_key = random.choice(list(service_types.keys()))
    random_value = service_types[random_key]
    return dict(service_class=random_key, service_name=random_value)


def prepare_address(address: Union[str, None]) -> Union[str, None]:
    """
    Функция для предобработки адреса

    Параметры
    ---------
    address: str, None
        адрес

    Возвращаемое значение
    ---------------------
    str, None
        оригинальное значение address или строка формата "Адрес: {address}"
    """
    if address is None:
        return address
    return "Адрес: {}".format(address) if len(address) != 0 else address


def get_clients_and_organizations_data(xlsx_obj: InMemoryUploadedFile) -> ClientsAndOrganizations:
    """
    Функция для получения данных клиентов и организаций из xlsx файла

    Параметры
    ---------
    xlsx_obj: InMemoryUploadedFile
        объект загруженного xlsx файла

    Возвращаемое значение
    ---------------------
    dict
        словарь с ключами clients_data и organizations_data,
        значения которых это список клиентов и данные об организациях соответственно
    """
    client_data = pd.read_excel(xlsx_obj, sheet_name="client")
    clients_data = client_data["name"].to_list()
    organization_data = pd.read_excel(xlsx_obj, sheet_name="organization")
    organizations_data = organization_data.to_dict('records')
    return dict(clients_data=clients_data, organizations_data=organizations_data)


def get_bills_data(xlsx_obj: InMemoryUploadedFile) -> List[Dict]:
    """
    Функция для получения данных счетов из xlsx файла

    Параметры
    ---------
    xlsx_obj: InMemoryUploadedFile
        объект загруженного xlsx файла

    Возвращаемое значение
    ---------------------
    dict
        словарь с данными о счетах
    """
    bills_data = pd.read_excel(xlsx_obj)
    bills_data = bills_data.to_dict('records')
    return bills_data
