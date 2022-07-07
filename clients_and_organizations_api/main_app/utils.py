import datetime
import random
from typing import TypedDict, List, Dict, Union

import pandas as pd
from django.core.files.uploadedfile import InMemoryUploadedFile
from pandas import Timestamp
from pydantic import BaseModel, validator


class BillsData(TypedDict):
    bill_obj: Union["BillObj1", "BillObj2", "BillObj3"]
    bills_data: List[Dict]


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


def fraud_detector() -> float:
    """
    Возвращает случайное значение в диапазоне от 0 до 1

    Возвращаемое значение
    ---------------------
    float
        случайное значение в диапазоне от 0 до 1
    """
    return random.random()


def service_classificator() -> ServiceClassificator:
    """
    Возвращает случайную пару ключ-значение из словаря service_types

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
    address = address.strip()
    address = address.strip('-')
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


def prepare_bill(bill_type: int, bill_data: Dict) -> Dict:
    """
    Функция для приведения разных структур словаря данных о счёте к общей структуре

    Параметры
    ---------
    bill_type: int
        список заголовков xlsx файла
    bill_data: Dict
        словарь с данными о счёте

    Возвращаемое значение
    ---------------------
    new_bill_data: Dict
        словарь с данными о счете с общей структурой
    """
    new_bill_data = {
        "client_name": None,
        "client_org": None,
        "number": None,
        "summ": None,
        "date": None,
        "service": None,
    }
    if bill_type == 1:
        new_bill_data["client_name"] = bill_data.get("client_name")
        new_bill_data["client_org"] = bill_data.get("client_org")
        new_bill_data["number"] = bill_data.get("№")
        new_bill_data["summ"] = bill_data.get("sum")
        new_bill_data["date"] = bill_data.get("date")
        new_bill_data["service"] = bill_data.get("service")
    elif bill_type == 2:
        new_bill_data["client_name"] = bill_data.get("client")
        new_bill_data["client_org"] = bill_data.get("organization")
        new_bill_data["number"] = bill_data.get("bill_number")
        new_bill_data["summ"] = bill_data.get("total_sum")
        new_bill_data["date"] = bill_data.get("created_date")
        new_bill_data["service"] = bill_data.get("service_name")
    else:
        new_bill_data["client_name"] = bill_data.get("client_code")
        new_bill_data["client_org"] = bill_data.get("client_org_name")
        new_bill_data["number"] = bill_data.get("number")
        new_bill_data["summ"] = bill_data.get("total")
        new_bill_data["date"] = bill_data.get("created")
        new_bill_data["service"] = bill_data.get("service")
    return new_bill_data


def get_bill_type(header: List) -> int:
    """
    Функция для определения типа структуры клиента

    Параметры
    ---------
    header: List
        список заголовков xlsx файла

    Возвращаемое значение
    ---------------------
    bill_type: int
        номер типа структуры клиента
    """
    if "client_name" in header and "client_org" in header:
        bill_type = 1
    elif "client" in header and "organization" in header:
        bill_type = 2
    else:
        bill_type = 3
    return bill_type


def get_bills_data(xlsx_obj: InMemoryUploadedFile) -> List[Dict]:
    """
    Функция для получения данных счетов из xlsx файла

    Параметры
    ---------
    xlsx_obj: InMemoryUploadedFile
        объект загруженного xlsx файла

    Возвращаемое значение
    ---------------------
    List[Dict]
        список словарей с данными о счетах
    """
    header = pd.read_excel(xlsx_obj, nrows=0).columns.to_list()
    bill_type = get_bill_type(header=header)
    bills_data = pd.read_excel(xlsx_obj)
    bills_data = bills_data.astype(object).where(pd.notnull(bills_data), None)
    bills_data = bills_data.to_dict('records')
    bills_data = [prepare_bill(bill_type=bill_type, bill_data=bill) for bill in bills_data]
    return bills_data


class BillObjModel(BaseModel):
    """
    Pydantic модель для валидации данных о счете
    """
    client_name: str
    client_org: str
    number: int
    summ: Union[int, float]
    date: Union[Timestamp, datetime.datetime, datetime.date]
    service: str

    @validator('client_name')
    def validate_client_name(cls, v):
        assert len(v.strip()) != 0, 'value must be not empty'
        return v

    @validator('client_org')
    def validate_client_org(cls, v):
        assert len(v.strip()) != 0, 'value must be not empty'
        return v

    @validator('service')
    def validate_service(cls, v):
        assert len(v.strip().strip("-")) != 0, 'value must be not empty'
        return v

    @validator('date', pre=True)
    def validate_date(cls, v):
        assert isinstance(v, (Timestamp, datetime.datetime, datetime.date)), 'value must be date'
        assert cls.valid_date(v), 'value must be date and contains year, month and day'
        return v

    @classmethod
    def valid_date(cls, date_obj: Timestamp) -> bool:
        datetime_obj = date_obj.date()
        if all(
                (hasattr(datetime_obj, 'year'), hasattr(datetime_obj, 'month'), hasattr(datetime_obj, 'day'))
        ):
            return True
        return False
