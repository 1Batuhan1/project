from django.db import models

# Create your models here.


class todo(models.Model):
    name = models.CharField(max_length=500, verbose_name="name")#karakter uzunluğunu ayarlarız.
    surname = models.CharField(max_length=500,verbose_name="surname")#verbose_name-->alan ismi
    age = models.CharField(max_length=50,verbose_name="age")
    
    def __str__(self):
       return "Name:"+self.name+"  "+"Surname:"+self.surname+"  "+"Age:"+str(self.age)
       
      #admin panelde object yerine başlığın isminin görünmesini sağlar.
       #return self.completed