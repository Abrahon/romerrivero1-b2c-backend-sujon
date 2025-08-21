from django.db import models

class CompanyCategory(models.TextChoices):
    IT = 'IT', 'IT'
    RETAIL = 'RETAIL', 'Retail'
    MANUFACTURING = 'MANUFACTURING', 'Manufacturing'
    EDUCATION = 'EDUCATION', 'Education'
    FINANCE = 'FINANCE', 'Finance'
    HEALTHCARE = 'HEALTHCARE', 'Healthcare'
    OTHER = 'OTHER', 'Other'

    @classmethod
    def choices(cls):
        return [(tag.name, tag.value) for tag in cls]

class ConnectionCategory(models.TextChoices):
    PARTNER = 'PARTNER', 'Partner'
    SUPPLIER = 'SUPPLIER', 'Supplier'
    CUSTOMER = 'CUSTOMER', 'Customer'
    DISTRIBUTOR = 'DISTRIBUTOR', 'Distributor'
    CONSULTANT = 'CONSULTANT', 'Consultant'
    OTHER = 'OTHER', 'Other'

    @classmethod
    def choices(cls):
        return [(tag.name, tag.value) for tag in cls]
