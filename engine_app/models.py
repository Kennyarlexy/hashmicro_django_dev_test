from django.db import models


class RoleChoices(models.IntegerChoices):
    MANAGER  = 1, "Manager"
    USER     = 2, "User"
    PUBLIC   = 3, "Public"


class InstalledModule(models.Model):
    name = models.CharField(max_length=64, unique=True, null=False, blank=False)


class Product(models.Model):
    name    = models.CharField(max_length=255, null=False, blank=False)
    barcode = models.ImageField(upload_to="barcodes/", blank=True, null=True)
    module  = models.ForeignKey(InstalledModule, on_delete=models.CASCADE, null=False)
    price   = models.DecimalField(max_digits=14, decimal_places=2, null=False, blank=False)
    stock   = models.PositiveIntegerField(null=False, blank=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name', 'module'], name='unique_product_per_module')
        ]


class AdditionalFieldDataType(models.IntegerChoices):
    INT    = 1, 'Integer'
    STRING = 2, 'String'


class AdditionalFieldMetadata(models.Model):
    name      = models.CharField(max_length=255, null=False, blank=False)
    data_type = models.PositiveSmallIntegerField(choices=AdditionalFieldDataType.choices, null=False)
    module    = models.ForeignKey(InstalledModule, null=False, on_delete=models.CASCADE)
    

class AdditionalFieldInt(models.Model):
    metadata = models.ForeignKey(AdditionalFieldMetadata, null=False, on_delete=models.CASCADE)
    product  = models.ForeignKey(Product, null=False, on_delete=models.CASCADE)
    value    = models.IntegerField(null=True, blank=True)


class AdditionalFieldStr(models.Model):
    metadata = models.ForeignKey(AdditionalFieldMetadata, null=False, on_delete=models.CASCADE)
    product  = models.ForeignKey(Product, null=False, on_delete=models.CASCADE)
    value    = models.CharField(max_length=255, null=True, blank=True)
