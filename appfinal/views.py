from django.shortcuts import render
from bs4 import BeautifulSoup
from django.db.models import Avg, Max, Min, Count
from django.template import RequestContext
from models import evento, Actualizacion, Usuario, relacion, CssUsuario
from operator import itemgetter,attrgetter
from django.template.loader import get_template 
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseNotFound,HttpResponseRedirect
from appfinal.forms import LoginForm
from xml.dom.minidom import parseString
from django.contrib.syndication.views import Feed
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
import feedparser 
import urllib2
import time
############################################################## FASE BETA ##############################################################


def CssOriginal():
    foriginal = open("static/css/TiposCssInvitado.css").read()
    fmodificado = open("static/css/TiposCss.css", "w")
    fmodificado.write(foriginal)
    fmodificado.close()
     
def CssModificado(UsuarioModificar):
    print UsuarioModificar
    valor = CssUsuario.objects.get(usuario = UsuarioModificar)
    fmodificar = open("static/css/TiposCss.css", "w")
    cambio = str("body{background: url(" + valor.ImagenFondo + ") no-repeat;background-color: " + valor.ColorFondo + "; color: " + valor.ColorLetra + ";font-size: " + valor.SizeLetra + "px;font-family: " + valor.TipoLetra + ";}")
    fmodificar.write(cambio);
    fmodificar.close();
    
def ayuda(request):
    login = False
    if request.user.is_authenticated():
        login = request.user     
    return render_to_response('ayuda.html', {'login':login},context_instance = RequestContext(request))
def logout_page(request):
    list = evento.objects.all()
    list.delete()
    CssOriginal()
    if request.user.is_authenticated():
        logout(request)
        salida = "Deslogueo completado" 
        form = LoginForm()
        return render_to_response('login.html', {'message':salida, 'form':form}, context_instance = RequestContext(request))     
    else:
        if request.method == "POST":          
            salida = logueo(request)
            form = LoginForm()
            if salida == "Identificacion Correcta":
                login = request.user
                CssModificado(login)
                return render_to_response('login.html', {'message':salida}, context_instance = RequestContext(request))
            else:
                return render_to_response('login.html', {'message':salida, 'form':form}, context_instance = RequestContext(request))
        else:
            salida = "No estas Logueado"
            form = LoginForm()
            return render_to_response('login.html', {'message':salida, 'form':form}, context_instance = RequestContext(request))
def login_page(request):
    message = None
    login = False 
    if request.user.is_authenticated():   
        print "Estas Logueado"
        salida = "Ya estas Logueado"
        login = request.user 
        return render_to_response('login.html', {'message':salida, 'login':login}, context_instance = RequestContext(request))
    else:
        if request.method == "POST":          
            salida = logueo(request)
            form = LoginForm()
            if salida == "Identificacion Correcta":
                login = request.user
                CssModificado(login)
                return render_to_response('login.html', {'message':salida, 'login':login}, context_instance = RequestContext(request))
            else:
                return render_to_response('login.html', {'message':salida, 'form':form}, context_instance = RequestContext(request))
        else:
            salida = "No estas Logueado"
            form = LoginForm()
            return render_to_response('login.html', {'message':salida, 'form':form}, context_instance = RequestContext(request))
def logueo(request):
        form = LoginForm(request.POST)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username = username, password = password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    message = "Identificacion Correcta"                    
                else:
                    message = "Usuario Inactivo"
            else:
                message = "Nombre de Usuario y/o incorrecto"
               
        return message    

############################################################## FASE ALPHA ##############################################################
def actividades(request, recurso):
    datos = None
    if (recurso == "/" or recurso == ""):
        return HttpResponseRedirect("/todas")
    else:
        mensaje = ""
        list = evento.objects.all()
        valor = recurso.split("/")[1]
        for i in list:
            if (str(i.id) == valor):
                mensaje = i
                if(i.masinformacion == "vacio"): 
                    try:
                        print "Descargando Informacion Extra...."            
                        file = urllib2.urlopen(i.url)
                        data = file.read()
                        file.close()   
                    except:
                        i.masinformacion = "vacio"
                        datos = i.masinformacion
                        i.save()
                    try:            
                        datos = data.split('<div class="parrafo">')[1].split('</div>')[0]
                        soup = BeautifulSoup(datos)
                        i.masinformacion = soup.get_text()
                        datos = i.masinformacion
                        i.save()
                    except:
                        i.masinformacion = "No hay informacion extra"
                        datos = i.masinformacion
                        i.save()
                    
                else:
                    datos = i.masinformacion
        if (mensaje == ""):
            mensaje = "No existe el valor pedido"
        
        
        return render_to_response('actividades.html', {'message': mensaje , 'masinformacion': datos}, context_instance = RequestContext(request))
    

        
@csrf_exempt
def todas(request,recurso):
      actualizados = 0
      antiguos = 0
      Totales = 0
      Actualizaciones = ""
      HoraActualizada = ""
      prueba = None
      login = False
      list = evento.objects.all()
      horaActualizada = Actualizacion.objects.all()
      lista = list.order_by('mes','dia')
      if request.path == "/actualizar":
        Dia = time.strftime("%d/%m/%y")
        Hora = time.strftime("%H:%M:%S")
        HoraActualizacion = Dia +  "-" + Hora
        if (len(horaActualizada) != 0):          
            for i in  range(len(horaActualizada)):           
                actualizo = Actualizacion.objects.get(id = horaActualizada[i].id)
                actualizo.hora =  HoraActualizacion
                actualizo.save()
        else:
            actualizo =  Actualizacion(hora = HoraActualizacion)
            actualizo.save()             
        [actualizados, antiguos] = actualizar()
        return HttpResponseRedirect("/todas")
      try:
          HoraActualizada = "Ultima Actualizacion: " + str(horaActualizada[0].hora)
      except:
          HoraActualizada = "Ultima Actualizacion: No hay Valor"  
      if request.method == "GET":
          antiguos = len(list)  
      if request.method == "POST":
          filtro = request.POST['filtro']
          parametro = request.POST['texto']
          eventos = None
          Info = "No hay Coincidencias, vuelva a intentarlo"
          if (filtro == "Nombre"):
              eventos = evento.objects.filter(nombre = parametro)            
          elif (filtro == "Tipo"):
              eventos = evento.objects.filter(tipo = parametro)
          elif (filtro == "Distrito"):
              eventos = evento.objects.filter(distrito = parametro.upper())
          elif(filtro == "Fecha"):
              parametros = parametro.split(" ")[0].split("/")
              dias = parametros[0]
              meses = parametros[1]
              anos = parametros[2]
              eventos = evento.objects.filter(dia = dias, mes = meses, ano = anos)
          if(len(eventos) != 0 ):
              Info = None
          if request.user.is_authenticated(): 
              login = request.user
             
         
              
          return render_to_response('todas.html', {'HoraActualizada': HoraActualizada , 'Actualizaciones': "TODAS LAS ACTIVIDAES: " ,'lista': eventos, 'Info': Info, 'login':login}, context_instance = RequestContext(request))
      
      Totales = len(evento.objects.all())
      if request.user.is_authenticated(): 
          login = request.user
          print request.user
      print recurso 
      if (recurso == "/rss"):
          doc = PasarAXmlTodas(lista)
          return HttpResponse(doc)
      return render_to_response('todas.html', {'HoraActualizada': HoraActualizada , 'Actualizaciones': "TODAS LAS ACTIVIDAES: " , 'Totales': Totales , 'lista': lista, 'login':login}, context_instance = RequestContext(request))

def apuntarse(request,recurso):
    datos = None
    tenemos = False;
    if (recurso == "/" or recurso == ""):
        return HttpResponseRedirect("/todas")
    else:
        mensaje = ""
        listEventos = evento.objects.all()
        listusuarios = Usuario.objects.all()
        listRelaciones = relacion.objects.all()
        valor = recurso.split("/")[1]
        userio = listusuarios.get(usuario = request.user)
        actividad = listEventos.get(id = valor)
        for i in range(len(listRelaciones)):
            if (listRelaciones[i].evento.id == actividad.id):
                tenemos = True
        if (tenemos != True):       
            print "no la tenemos"
            Dia = time.strftime("%d/%m/%y")
            Hora = time.strftime("%H:%M:%S")
            parametros = Dia.split(" ")[0].split("/")
            dias = parametros[0]
            meses = parametros[1]
            anos = "20" + parametros[2]
            parametros = Hora.split(" ")[0].split(":")
            horas = parametros[0] + ":00" 
            seleccionada = dias + "/" + meses + "/" + anos + " - " + Hora
            nuevo = relacion(user = request.user, evento = actividad, fechaElgida = str(seleccionada))
            nuevo.save()
            userio.eventos.add(nuevo)
            userio.save() 
            print nuevo.fechaElgida
    return HttpResponseRedirect("/todas")

@csrf_exempt
def inicio(request,recurso):
    print request.user.is_authenticated()
    if (request.user.is_authenticated() == False):
        CssOriginal()
    if (recurso == "/" or recurso == "" or recurso =="rss"):
          print request.method
          mensaje = None
          prueba = None
          login = False
          nuevalista = []
          Dia = time.strftime("%d/%m/%y")
          Hora = time.strftime("%H:%M:%S")
          parametros = Dia.split(" ")[0].split("/")
          dias = parametros[0]
          meses = parametros[1]
          anos = "20" + parametros[2]
          parametros = Hora.split(" ")[0].split(":")
          horas = parametros[0] + ":00"    
          list = evento.objects.all()
          for i in range(len(list)):
              if (anos <= list[i].ano):
                  if (meses <= list[i].mes):
                      if(dias <= list[i].dia):
                          if ( dias == list[i].dia and meses == list[i].mes and anos == list[i].ano):
                              if(horas < list[i].hora):
                                  nuevalista.append(list[i])
                          else:
                              nuevalista.append(list[i])
          lista = list.order_by('mes','dia') 
          lista = sorted(nuevalista, key=attrgetter('mes','dia','hora'))
          if (recurso =="rss"):
              doc = PasarAXmlTodas(lista[0:10])
              return HttpResponse(doc)
          listUsuarios = Usuario.objects.all()
          if request.user.is_authenticated(): 
              login = request.user
              print request.user
          return render_to_response('inicio.html', {'message': mensaje, 'lista': lista[0:10], 'listaUsuarios': listUsuarios, 'login':login}, context_instance = RequestContext(request))
    else:
        if request.method == "POST":
            filtro = request.POST['css']
            parametro = request.POST['texto']
            CambiarCss(filtro, parametro, request.user)
        lista = []
        login = False
        list = Usuario.objects.all()   
        if(len(recurso.split("/")) == 2):
            xml = recurso.split("/")[1]
            if(xml == "rss"):
                valor = recurso.split("/")[0]
                for i in list:
                    if(str(i.usuario) == str(valor)):
                        lista = i
                        doc = PasarAXml(lista)
                        return HttpResponse(doc)
            elif(xml == "Page2"):
                valor = recurso.split("/")[0]
                if request.user.is_authenticated(): 
                    login = request.user     
                    for i in list:
                        if (str(i.usuario) == str(valor)): 
                            usuarioCompleto = i 
                            for j in i.eventos.all():   
                                lista.append(j)
                            return render_to_response('usuarios.html', {'actividades': lista[10:20] ,'usuario': usuarioCompleto, 'login':login, 'valor':valor}, context_instance = RequestContext(request))
            elif(xml == "Page3"):
                valor = recurso.split("/")[0]
                if request.user.is_authenticated(): 
                    login = request.user     
                    for i in list:
                        if (str(i.usuario) == str(valor)):
                            usuarioCompleto = i 
                            for j in i.eventos.all():
                                lista.append(j)
                            return render_to_response('usuarios.html', {'actividades': lista[20:30] ,'usuario': usuarioCompleto, 'login':login, 'valor':valor}, context_instance = RequestContext(request))
            elif(xml == "Page4"):
                valor = recurso.split("/")[0]
                if request.user.is_authenticated(): 
                    login = request.user     
                    for i in list:
                        if (str(i.usuario) == str(valor)): 
                            usuarioCompleto = i 
                            for j in i.eventos.all():   
                                lista.append(j)
                            return render_to_response('usuarios.html', {'actividades': lista[30:40] ,'usuario': usuarioCompleto, 'login':login, 'valor':valor}, context_instance = RequestContext(request))

            else:
                valor = recurso.split("/")[0]
                return HttpResponseRedirect("/"+valor)
        else:
            valor = recurso.split("/")[0]              
            if request.user.is_authenticated(): 
                login = request.user     
            for i in list:
                if (str(i.usuario) == str(valor)):
                    usuarioCompleto = i
                    for j in i.eventos.all():   
                        lista.append(j)
                    return render_to_response('usuarios.html', {'actividades': lista[0:10], 'usuario': usuarioCompleto, 'login':login, 'valor':valor}, context_instance = RequestContext(request))
            return render_to_response('usuarios.html', {'usuario': lista }, context_instance = RequestContext(request))   

def actualizar():
  
    contadorActualizado = 0
    contadorAntiguo = 0
    nombre = " "
    tipo = " "
    fecha = " "
    hora = " "
    descripcion = " "
    largaduracion = " "
    localizaciones = " "
    longitud = " "
    latitud = " "
    localidad = " "
    distrito = " "
    url = " "
    precio = " "
    try:
      print "Descargando Fichero Espere...." 
      file = urllib2.urlopen('http://datos.madrid.es/egob/catalogo/206974-0-agenda-eventos-culturales-100.xml')
      data = file.read()
      file.close()
      salida = []
      dom = parseString(data)
      print "Descarga Finalizada... Ficheros encontrados: " + str(dom.getElementsByTagName('contenido').length)
      print "Estamos Colocando los Datos...Espere"
      contenido = dom.getElementsByTagName('contenido')
      if(dom.getElementsByTagName('contenido').length > 0):
        for number in range(dom.getElementsByTagName('contenido').length):
            contenidoList = contenido[number].getElementsByTagName('atributos')[0].getElementsByTagName('atributo')
            nombre = " "
            tipo = " "
            fecha = " "
            hora = " "
            descripcion = "No hay Descripcion"
            largaduracion = " "
            localizaciones = " "
            longitud = " "
            latitud = " "
            localidad = " "
            distrito = " "
            url = " "
            precio = " "
            for eventos in range(len(contenidoList)):              
                if contenidoList[eventos].attributes['nombre'].value == "TITULO":
                    nombres = contenidoList[eventos].firstChild.nodeValue
                elif contenidoList[eventos].attributes['nombre'].value == "TIPO":
                    tipo = contenidoList[eventos].firstChild.nodeValue
                elif contenidoList[eventos].attributes['nombre'].value == "FECHA-EVENTO":
                    fecha = contenidoList[eventos].firstChild.nodeValue
                elif contenidoList[eventos].attributes['nombre'].value == "HORA-EVENTO":
                    hora = contenidoList[eventos].firstChild.nodeValue
                elif contenidoList[eventos].attributes['nombre'].value == "LOCALIZACION":
                    localizacion = contenidoList[eventos].childNodes
                    for lugar in range(len(localizacion)): 
                        try:                                        
                            if localizacion[lugar + 1].attributes['nombre'].value == "NOMBRE-INSTALACION":
                                localizaciones = localizacion[lugar+1].firstChild.nodeValue
                            elif localizacion[lugar + 1].attributes['nombre'].value == "LATITUD":
                                latitud = localizacion[lugar+1].firstChild.nodeValue
                            elif localizacion[lugar + 1].attributes['nombre'].value == "LONGITUD":
                                longitud = localizacion[lugar+1].firstChild.nodeValue  
                            elif localizacion[lugar + 1].attributes['nombre'].value == "LOCALIDAD":
                                localidad = localizacion[lugar+1].firstChild.nodeValue
                            elif localizacion[lugar + 1].attributes['nombre'].value == "DISTRITO":
                                distrito = localizacion[lugar+1].firstChild.nodeValue  
                        except:
                            continue
                elif contenidoList[eventos].attributes['nombre'].value == "EVENTO-LARGA-DURACION":
                    if contenidoList[eventos].firstChild.nodeValue == "0":
                        largaduracion = "Evento de Corta Duracion"
                    else:
                        largaduracion = "Evento de Larga Duracion"
                elif contenidoList[eventos].attributes['nombre'].value == "GRATUITO":
                    precio = " "
                    if contenidoList[eventos].firstChild.nodeValue == "0":
                        for precios in range(len(contenidoList)): 
                            if contenidoList[precios].attributes['nombre'].value == "PRECIO":
                                precio = contenidoList[precios].firstChild.nodeValue
                        if (precio == " "): 
                            precio = "No hay informacion"
                    else:
                        precio = "Gratuito"
                elif contenidoList[eventos].attributes['nombre'].value == "DESCRIPCION":
                    descripcion = contenidoList[eventos].firstChild.nodeValue
                elif contenidoList[eventos].attributes['nombre'].value == "CONTENT-URL-ACTIVIDAD":
                    url = contenidoList[eventos].firstChild.nodeValue
            valor = def_eventos(nombres, tipo, precio, fecha, hora, largaduracion, url, localizaciones, latitud, longitud, localidad, distrito, descripcion)
            if(valor == "OK"):
                contadorActualizado = contadorActualizado + 1
            else:
              contadorAntiguo = contadorAntiguo + 1  
      else:
        contadorActualizado = 0
        contadorAntiguo = 0
        print "El fichero esta vacio, Contacte con la Web de la Comunidad de Madrid" 
        return [contadorActualizado, dom.getElementsByTagName('contenido').length]
    except BufferError:
        print "Error en la descarga, Avise al Administrador" 
    print "Finalizado!!"
    return [contadorActualizado, contadorAntiguo]
    
    
def def_eventos(titulo, tipos, precios, fechas, horas, largaduracion, urls, localizaciones, latitud, longitud, localidad, distrito, descripciones):
    list = evento.objects.all()
    tipados = "No hay Datos"
    fecha = fechas.split(" ")[0].split("-")
    fechados = fecha[2] + "-" + fecha[1] + "-"  + fecha[0]
    dia = fecha[2] 
    mes = fecha[1]
    ano = fecha[0]
    if(tipos != " "):
        tipados = tipos.split("/")[3]
    resultado = "OK"  
    try:
        elemento = list.get(nombre = titulo, dia = dia, mes = mes, ano = ano, hora = horas)
        resultado = "FAIL"
    except:       
        nuevo = evento(nombre = titulo, tipo = tipados, precio = precios,  dia = dia, mes = mes, ano = ano, hora = horas, duracion = largaduracion, url = urls, localizacion = localizaciones, latitud = latitud, longitud = longitud, localidad = localidad, distrito = distrito , masinformacion = "vacio", descripcion = descripciones) 
        nuevo.save()   
    return resultado
    
def PasarAXml(usuario):
    doc = "<?xml version='1.0' encoding='utf-8'?><rss xmlns:atom='http://www.w3.org/2005/Atom' version='2.0'><channel><title>Descubre Madrid</title><link>http://localhost:8000</link><description>Canal RSS con todas las Actividades de " + str(usuario.usuario) + "</description><atom:link href='http://localhost:8000/" + str(usuario.usuario) + "/rss/' rel='self'></atom:link><language>en-us</language>"
    for i in usuario.eventos.all():
        doc += "<item><title>" + i.evento.nombre  + "</title><description>" + i.evento.descripcion + "</description><guid>http://localhost:8000/actividades/" + str(i.evento.id) + "</guid><pubDate> " +  str(i.evento.mes) + " " + str(i.evento.dia) + " "+ str(i.evento.ano) + " </pubDate></item>" 
    return doc
def PasarAXmlTodas(usuario):
    doc = "<?xml version='1.0' encoding='utf-8'?><rss xmlns:atom='http://www.w3.org/2005/Atom' version='2.0'><channel><title>Descubre Madrid</title><link>http://localhost:8000</link><description>Canal RSS con todas las Actividades</description><atom:link href='http://localhost:8000/rss/' rel='self'></atom:link><language>en-us</language>"
    print usuario
    for i in usuario:
        doc += "<item><title>" + i.nombre  + "</title><description>" + i.descripcion + "</description><guid>http://localhost:8000/actividades/" + str(i.id) + "</guid><pubDate> " +  str(i.mes) + " " + str(i.dia) + " "+ str(i.ano) + " </pubDate></item>" 
    return doc   
    
def CambiarCss(Tipo, Parametro, Usuario):
    valor = CssUsuario.objects.get(usuario = Usuario)  
    if (Tipo == "Color Fondo"):
        valor.ColorFondo =  Parametro          
    elif (Tipo == "Imagen Fondo"):
        valor.ImagenFondo =  Parametro
    elif (Tipo == "Color Letra"):
        valor.ColorLetra =  Parametro 
    elif(Tipo == "Size Letra"):
        valor.SizeLetra =  Parametro 
    elif(Tipo == "Tipo Letra"):
        valor.TipoLetra =  Parametro
    valor.save()
    CssModificado(Usuario)