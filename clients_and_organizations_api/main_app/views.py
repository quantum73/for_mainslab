from django.db.models import Count, Sum, F
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.exceptions import UnsupportedMediaType
from rest_framework.response import Response

from main_app import models
from main_app import utils
from main_app.models import Client, Organization, Bill
from main_app.serializers import ClientSerializer, BillSerializer


class ClientsViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    ClientsViewSet - вьюсет для выдачи списка клиентов и для загрузки данных о клиентах и их организациях
    """
    serializer_class = ClientSerializer
    queryset = models.Client.objects.prefetch_related("organizations", "bill")

    def get_queryset(self):
        """
        Переопределенный метод get_queryset с аннотацией для агрегации данных клиента:
        1. organizations_count - количество всех организаций, принадлежащих клиенту
        2. all_sums - сумма по счетам всех организаций клиента
        """
        return models.Client.objects.annotate(
            organizations_count=Count('organizations'),
            all_sums=Sum('bill__summ'),
        )

    @action(
        methods=["post"],
        detail=False,
        url_path="upload",
        url_name="upload_clients_data",
    )
    def upload_xlsx(self, request):
        """
        Метод upload_xlsx предназначен для загрузки данных о клиентах и их организациях из .xlsx файла в базу данных.

        Метод ожидает в теле POST запроса поле file с прикрепленным файлом в формате .xlsx.
        - Если файла нет - возвращается ответ со статус-кодом 400 и сообщением, что поле file пустое.
        - Если файл не в формате .xlsx - возвращается ответ со статус-кодом 415 и сообщением,
        что файл должен быть с расширением .xlsx.
        - Если все хорошо, то возвращается пустой ответ со статус-кодом 201
        """
        file_obj = request.FILES.get('file')
        if not file_obj:
            return Response(
                dict(detail="Empty \"file\" field"),
                status=status.HTTP_400_BAD_REQUEST
            )
        if not file_obj.name.endswith(".xlsx"):
            raise UnsupportedMediaType(file_obj.content_type, detail="File must be .xlsx")

        data = utils.get_clients_and_organizations_data(file_obj)
        clients_data = data.get("clients_data")
        organizations_data = data.get("organizations_data")

        clients = [Client(name=client_name) for client_name in clients_data]
        Client.objects.bulk_create(clients)

        organizations = []
        for client_obj in Client.objects.all():
            orgs = list(filter(lambda x: x.get("client_name") == client_obj.name, organizations_data))
            organizations.extend(
                list(
                    map(
                        lambda x: Organization(
                            name=x.get("name"),
                            address=utils.prepare_address(x.get("address")),
                            client=client_obj,
                        ),
                        orgs
                    )
                )
            )
        Organization.objects.bulk_create(organizations)

        return Response(status=status.HTTP_201_CREATED)


class BillsViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    BillsViewSet - вьюсет для выдачи списка счетов и для загрузки данных о счетах.
    Есть возможность фильтрации счетов по имени клиента и имени организации с помощью query-параметров.
    """
    serializer_class = BillSerializer
    queryset = models.Bill.objects.select_related("client", "organization")

    def get_queryset(self):
        """
        Переопределенный метод get_queryset, который фильтрует queryset по имени клиента
         и/или по имени организации.
        Фильтры передаются в качестве query-параметров client и organization соответственно.
        """
        queryset = super().get_queryset()
        client = self.request.query_params.get('client')
        organization = self.request.query_params.get('organization')
        if client is not None and organization is not None:
            queryset = queryset.filter(client__name=client, organization__name=organization)
        elif client is not None:
            queryset = queryset.filter(client__name=client)
        elif organization is not None:
            queryset = queryset.filter(organization__name=organization)
        return queryset

    @action(
        methods=["post"],
        detail=False,
        url_path="upload",
        url_name="upload_bills_data",
    )
    def upload_xlsx(self, request):
        """
        Метод upload_xlsx предназначен для загрузки данных о счетах из .xlsx файла в базу данных.

        Метод ожидает в теле POST запроса поле file с прикрепленным файлом в формате .xlsx.
        - Если файла нет - возвращается ответ со статус-кодом 400 и сообщением, что поле file пустое.
        - Если файл не в формате .xlsx - возвращается ответ со статус-кодом 415 и сообщением,
        что файл должен быть с расширением .xlsx.
        - Если все хорошо, то возвращается пустой ответ со статус-кодом 201
        """
        file_obj = request.FILES.get('file')
        if not file_obj:
            return Response(
                dict(detail="Empty \"file\" field"),
                status=status.HTTP_400_BAD_REQUEST
            )
        if not file_obj.name.endswith(".xlsx"):
            raise UnsupportedMediaType(file_obj.content_type, detail="File must be .xlsx")

        bills_data = utils.get_bills_data(file_obj)
        bills = []
        for bill in bills_data:
            client_name = bill.get("client_name")
            organization_name = bill.get("client_org")
            client_obj = Client.objects.filter(name=client_name)
            if not client_obj.exists():
                continue
            organization_obj = Organization.objects.filter(name=organization_name)
            if not organization_obj.exists():
                continue

            fraud_score = utils.fraud_detector()
            if fraud_score >= 0.9:
                organization_obj.update(fraud_weight=F('fraud_weight') + 1)

            service_classificator = utils.service_classificator()
            client_obj = client_obj.first()
            organization_obj = organization_obj.first()
            bills.append(
                Bill(
                    number=bill.get("№"),
                    summ=bill.get("sum"),
                    date=bill.get("date"),
                    service=bill.get("service"),
                    fraud_score=fraud_score,
                    service_class=service_classificator.get("service_class"),
                    service_name=service_classificator.get("service_name"),
                    client=client_obj,
                    organization=organization_obj,
                )
            )
        Bill.objects.bulk_create(bills)

        return Response(status=status.HTTP_201_CREATED)
