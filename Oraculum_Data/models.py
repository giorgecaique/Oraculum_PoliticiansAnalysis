from django.db import models

class user(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    username = models.CharField(max_length=30)
    password = models.CharField(max_length=30) 
    street = models.CharField(max_length=30)
    number = models.IntegerField()
    neighborhood = models.CharField(max_length=30)
    city = models.CharField(max_length=30)
    estate = models.CharField(max_length=30)
    cep = models.CharField(max_length=30) 
    email = models.CharField(max_length=30)
    
    def __init__(self, first_name, last_name,username, password, street, number, neighborhood, city, estate, cep, email):
        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        self.password = password
        self.street = street
        self.number = number
        self.neighborhood = neighborhood,
        self.city = city
        self.estate = estate
        self.cep = cep
        self.email = email