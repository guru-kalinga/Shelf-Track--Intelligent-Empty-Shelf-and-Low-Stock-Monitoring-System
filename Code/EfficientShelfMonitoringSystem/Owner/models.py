from django.db import models

# Create your models here.
class Employee_Enrol (models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name