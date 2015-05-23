from django.db import models
from django.contrib.auth.models import User
from django.contrib.syndication.views import Feed

# Create your models here.
class evento(models.Model):
  nombre = models.TextField()
  tipo = models.TextField()
  precio = models.TextField()
  dia = models.TextField();
  mes = models.TextField();
  ano = models.TextField();
  duracion = models.TextField()
  url = models.TextField()
  masinformacion = models.TextField()
  descripcion = models.TextField()  
  localizacion = models.TextField()
  latitud = models.TextField()
  longitud = models.TextField()
  localidad = models.TextField()
  distrito = models.TextField()
  hora = models.TextField()

class relacion(models.Model):
  user = models.ForeignKey(User)
  evento = models.ForeignKey(evento)
  fechaElgida = models.TextField()
  
class Usuario (models.Model):
  usuario = models.OneToOneField(User)
  titulo = models.TextField()
  descripcion = models.TextField()
  eventos = models.ManyToManyField(relacion,blank=True)

class CssUsuario (models.Model):
	usuario = models.OneToOneField(User)
	ColorLetra = models.TextField()
	TipoLetra = models.TextField()
	ColorFondo= models.TextField()
	ImagenFondo = models.TextField()
	SizeLetra = models.TextField()

  
class Actualizacion(models.Model):
  hora = models.TextField()
  
