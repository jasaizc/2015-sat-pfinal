from django.contrib import admin
from models import Usuario, evento, Actualizacion, relacion ,CssUsuario

# Register your models here.
admin.site.register(Usuario)
admin.site.register(evento)
admin.site.register(Actualizacion)
admin.site.register(relacion)
admin.site.register(CssUsuario)