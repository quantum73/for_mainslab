from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class Client(models.Model):
    name = models.CharField(max_length=128, unique=True, verbose_name="client_name")

    class Meta:
        verbose_name = "client"
        verbose_name_plural = "clients"

    def __str__(self):
        return self.name


class Organization(models.Model):
    name = models.CharField(max_length=256, verbose_name="organization_name")
    address = models.CharField(max_length=1024, verbose_name="organization_address")
    fraud_weight = models.IntegerField(default=0, verbose_name="fraud_weight")
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name="organizations",
        verbose_name="client_name"
    )

    class Meta:
        verbose_name = "organization"
        verbose_name_plural = "organizations"
        unique_together = ('name', 'client',)

    def __str__(self):
        return self.name


class Bill(models.Model):
    number = models.IntegerField(verbose_name="number")
    summ = models.IntegerField(validators=[MinValueValidator(0)], verbose_name="summ")
    date = models.DateField(verbose_name="date")
    service = models.TextField(verbose_name="service_description")
    fraud_score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        verbose_name="fraud_weight"
    )
    service_class = models.IntegerField(validators=[MinValueValidator(0)], verbose_name="service_class")
    service_name = models.CharField(max_length=128, verbose_name="service_name")
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name="bill",
        verbose_name="client's_bill"
    )
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="bill",
        verbose_name="organization's_bill"
    )

    class Meta:
        verbose_name = "bill"
        verbose_name_plural = "bills"
        unique_together = ('number', 'organization',)

    def __str__(self):
        return "Bill №{}".format(self.number)
