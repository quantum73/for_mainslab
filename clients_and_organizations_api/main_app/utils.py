import random
from abc import ABC
from typing import TypedDict, List, Dict, Union

import pandas as pd
from django.core.files.uploadedfile import InMemoryUploadedFile
from pandas import Timestamp


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


def get_bills_obj_and_data(xlsx_obj: InMemoryUploadedFile) -> BillsData:
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
    header = pd.read_excel(xlsx_obj, nrows=0).columns.to_list()
    if "client_name" in header and "client_org" in header:
        bill_obj = BillObj1
    elif "client" in header and "organization" in header:
        bill_obj = BillObj2
    else:
        bill_obj = BillObj3
    bills_data = pd.read_excel(xlsx_obj)
    bills_data = bills_data.to_dict('records')
    return {"bill_obj": bill_obj, "bills_data": bills_data}


class AbstractBillObj(ABC):
    def __init__(self, data: Dict, idx_row: int = None) -> None:
        self._data = data
        self._idx_row = idx_row
        self._obj_is_valid = True
        self._errors = []
        self._validated_data = None

    def is_valid(self) -> bool:
        pass

    def eval(self) -> None:
        pass

    def errors(self) -> Dict:
        pass

    def validated_data(self) -> Dict:
        pass


class BaseBillObj(AbstractBillObj):
    def __init__(self, data: Dict) -> None:
        super().__init__(data)

    def is_valid(self) -> bool:
        self.eval()
        return self._obj_is_valid

    def eval(self) -> None:
        pass

    def valid_date(self, date_obj) -> bool:
        date = date_obj.date()
        if all((hasattr(date, 'year'), hasattr(date, 'month'), hasattr(date, 'day'))):
            return True
        return False

    @property
    def errors(self) -> Union[List[Dict], None]:
        if not self._obj_is_valid:
            return self._errors

    @property
    def validated_data(self) -> Union[Dict, None]:
        if self._obj_is_valid:
            return self._validated_data


class BillObj1(BaseBillObj):
    def __init__(self, data: Dict) -> None:
        super().__init__(data)

    def eval(self) -> None:
        client_name = self._data.get("client_name")
        client_org = self._data.get("client_org")
        number = self._data.get("№")
        summ = self._data.get("sum")
        date = self._data.get("date")
        service = self._data.get("service")
        self._validated_data = {
            "client_name": client_name,
            "client_org": client_org,
            "number": number,
            "summ": summ,
            "date": date,
            "service": service,
        }
        if not isinstance(summ, (int, float)):
            self._obj_is_valid = False
            self._errors.append(
                {
                    "field": "sum",
                    "message": "Поле sum должно быть числом",
                }
            )
        if not isinstance(number, int):
            self._obj_is_valid = False
            self._errors.append(
                {
                    "field": "№",
                    "message": "Поле № должно быть числом",
                }
            )
        if not isinstance(service, str) or len(service.strip().strip("-")) == 0:
            self._obj_is_valid = False
            self._errors.append(
                {
                    "field": "service",
                    "message": "Поле service должно быть непустым (пусто так же считается, если вместо текста знак “-”)",
                }
            )
        if client_name is None or not isinstance(client_name, str) or not client_name.strip():
            self._obj_is_valid = False
            self._errors.append(
                {
                    "field": "client_name",
                    "message": "Поле client_name должно быть непустым",
                }
            )
        if client_org is None or not isinstance(client_org, str) or not client_org.strip():
            self._obj_is_valid = False
            self._errors.append(
                {
                    "field": "client_org",
                    "message": "Поле client_org должно быть непустым",
                }
            )
        if date is None or not isinstance(date, Timestamp) or not self.valid_date(date):
            self._obj_is_valid = False
            self._errors.append(
                {
                    "field": "date",
                    "message": "Поле date должно являться датой и содержать день, месяц и год",
                }
            )


class BillObj2(BaseBillObj):
    def __init__(self, data: Dict) -> None:
        super().__init__(data)

    def eval(self) -> None:
        client_name = self._data.get("client")
        client_org = self._data.get("organization")
        number = self._data.get("bill_number")
        summ = self._data.get("total_sum")
        date = self._data.get("created_date")
        service = self._data.get("service_name")
        self._validated_data = {
            "client_name": client_name,
            "client_org": client_org,
            "number": number,
            "summ": summ,
            "date": date,
            "service": service,
        }
        if not isinstance(summ, (int, float)):
            self._obj_is_valid = False
            self._errors.append(
                {
                    "field": "total_sum",
                    "message": "Поле total_sum должно быть числом",
                }
            )
        if not isinstance(number, int):
            self._obj_is_valid = False
            self._errors.append(
                {
                    "field": "bill_number",
                    "message": "Поле bill_number должно быть числом",
                }
            )
        if not isinstance(service, str) or len(service.strip().strip("-")) == 0:
            self._obj_is_valid = False
            self._errors.append(
                {
                    "field": "service_name",
                    "message": "Поле service_name должно быть непустым (пусто так же считается, если вместо текста знак “-”)",
                }
            )
        if client_name is None or not isinstance(client_name, str) or not client_name.strip():
            self._obj_is_valid = False
            self._errors.append(
                {
                    "field": "client",
                    "message": "Поле client должно быть непустым",
                }
            )
        if client_org is None or not isinstance(client_org, str) or not client_org.strip():
            self._obj_is_valid = False
            self._errors.append(
                {
                    "field": "organization",
                    "message": "Поле organization должно быть непустым",
                }
            )
        if date is None or not isinstance(date, Timestamp) or not self.valid_date(date):
            self._obj_is_valid = False
            self._errors.append(
                {
                    "field": "created_date",
                    "message": "Поле created_date должно являться датой и содержать день, месяц и год",
                }
            )


class BillObj3(BaseBillObj):
    def __init__(self, data: Dict) -> None:
        super().__init__(data)

    def eval(self) -> None:
        client_name = self._data.get("client_code")
        client_org = self._data.get("client_org_name")
        number = self._data.get("number")
        summ = self._data.get("total")
        date = self._data.get("created")
        service = self._data.get("service")
        self._validated_data = {
            "client_name": client_name,
            "client_org": client_org,
            "number": number,
            "summ": summ,
            "date": date,
            "service": service,
        }
        if not isinstance(summ, (int, float)):
            self._obj_is_valid = False
            self._errors.append(
                {
                    "field": "total",
                    "message": "Поле total должно быть числом",
                }
            )
        if not isinstance(number, int):
            self._obj_is_valid = False
            self._errors.append(
                {
                    "field": "number",
                    "message": "Поле number должно быть числом",
                }
            )
        if not isinstance(service, str) or len(service.strip().strip("-")) == 0:
            self._obj_is_valid = False
            self._errors.append(
                {
                    "field": "service",
                    "message": "Поле service должно быть непустым (пусто так же считается, если вместо текста знак “-”)",
                }
            )
        if client_name is None or not isinstance(client_name, str) or not client_name.strip():
            self._obj_is_valid = False
            self._errors.append(
                {
                    "field": "client_code",
                    "message": "Поле client_code должно быть непустым",
                }
            )
        if client_org is None or not isinstance(client_org, str) or not client_org.strip():
            self._obj_is_valid = False
            self._errors.append(
                {
                    "field": "client_org_name",
                    "message": "Поле client_org_name должно быть непустым",
                }
            )
        if date is None or not isinstance(date, Timestamp) or not self.valid_date(date):
            self._obj_is_valid = False
            self._errors.append(
                {
                    "field": "created",
                    "message": "Поле created должно являться датой и содержать день, месяц и год",
                }
            )
