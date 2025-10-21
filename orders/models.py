from django.db import models
import uuid
# Create your models here.

class Status(models.TextChoices):
    PENDING = "pending", "Pending"
    PROCESSING = "processing", "Processing"
    COMPLETED = "completed", "Completed"
    CANCELLED = "cancelled", "Cancelled"

class Order(models.Model):
    id = models.AutoField(primary_key=True)
    uid = models.CharField(max_length=255, unique=True, default=uuid.uuid4)
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, related_name='orders')
    product_name = models.CharField(max_length=255)
    quantity = models.IntegerField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50, choices=Status.choices, default=Status.PENDING, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True, db_index=True)