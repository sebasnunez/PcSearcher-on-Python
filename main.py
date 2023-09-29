from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
import os
import wget
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './temp'
import subprocess
@app.route("/", methods = ["POST"])
def recorrerIp():
  if request.method=="POST" and 'recorrer' in request.form:
    ip = request.form.get("ip")
    listIp = []
    resIp = subprocess.Popen("nmap -sP "+ip+".0/24", shell=True, stdout=subprocess.PIPE)
    outIp = resIp.stdout.read()
    l1 = []
    for x in str(outIp).split("\\n"):
      l1.append(str(x))
    for x in l1:
      if x[0]=="N" and x[5]=="s":
        n = str(x[21:-2])
        if len(n) >15:
          listIp.append(n.split(" (")[1][:-1])
          print(n.split(" (")[1][:-1])
        else:
          listIp.append(n)
          print(n)
    listT = []
    for x in listIp:
      resH = subprocess.Popen("wmic /node:'"+x+"' os get csname", shell=True, stdout=subprocess.PIPE)
      outH = resH.stdout.read()
      if str(outH)[2] != "C":
        resH = subprocess.Popen("cd ./pstools && PsExec \\\\"+x+" hostname", shell=True, stdout=subprocess.PIPE)
        outH = resH.stdout.read()
        if str(outH)[-18]=="r":
          print("Error de Conexion con la ip "+x)
        else:
          listT.append(x+": "+str(outH)[138:-5])
      else:
        listT.append(x+": "+str(outH)[23:-15])
    file = open("./historico/"+ip+".txt","w")
    for x in listT:
      file.write(x+"\n")
    file.close()
    listaD = listar()
    return render_template("index.html", nElementos = len(listT),names = listT, opcion = listaD)
  else:
    if request.method=="POST" and 'historicoRecorrido' in request.form:
      des = request.form.get("des")
      file = open("./historico/"+str(des) + ".txt", "r")
      ls = []
      for x in file:
        ls.append(x)
      file.close()
      listaD = listar()
      return render_template("index.html",nElementos = len(ls), names = ls, opcion = listaD)
    else:
      if request.method=="POST" and 'botonEvidencia' in request.form:
        ip = request.form.get("evidencia")
        res = subprocess.Popen("ping -n 1 "+str(ip), shell=True,stdout=subprocess.PIPE)
        out = res.stdout.read()
        if str(out)[-6]=="s":
          tipo = request.form.get("TiEq")
          evidencia = open("./evidencia.bat", "w")
          if str(tipo)=="escritorio":
            evidencia.write('cd pstools\nPsExec \\\\'+str(ip)+' cmd /c (ipconfig/all ^&  PowerShell "Get-PhysicalDisk | Format-Table -AutoSize" ^& wmic memorychip get capacity, manufacturer ^& wmic product where name="Ivanti Notifications Manager" get name, version ^& wmic product where name="Trend Micro Apex One Security Agent" get name, version ^& cd "c:\Program Files (x86)\LANDesk\LDClient" ^& start /B /MIN vulscan.exe ^& start /B /MIN LDISCN32.exe)')
          else:
            evidencia.write('cd pstools\nPsExec \\\\'+str(ip)+' cmd /c (ipconfig/all ^&  PowerShell "Get-PhysicalDisk | Format-Table -AutoSize" ^& wmic memorychip get capacity, manufacturer ^& wmic product where name="Ivanti Notifications Manager" get name, version ^& wmic product where name="Trend Micro Apex One Security Agent" get name, version ^& cd "c:\Program Files (x86)\LANDesk\LDClient" ^& start /B /MIN vulscan.exe ^& start /B /MIN LDISCN32.exe ^& manage-bde -status)')
          res = subprocess.run("start evidencia.bat", shell=True)
          listaD = listar()
          return render_template('index.html', opcion = listaD)
        else:
          listaD = listar()
          return render_template('index.html', opcion = listaD, ip=ip)
      else:
        if request.method=="POST" and 'botonEqui' in request.form:
          nombreEqui = request.form.get("nombreEqui")
          archivo = request.form.get("archivoSubido")
          if nombreEqui!="" and archivo is None:
            Equi = "Equipo encontrado:\n"
            res = subprocess.Popen('cd ./historico/ && find "'+str(nombreEqui)+'" ./*.txt', shell=True,stdout=subprocess.PIPE)
            out = res.stdout.read()
            if 'n1' in str(out):
              nombre="1"+str(out).split('n1')[1]
              n = 1
              while True:
                if nombre[n]=="\\":
                  break
                n+=1
              nombre=nombre[:n]
              Equi += nombre
            else:
              Equi = 'El equipo no se encuentra en ninguna consulta'
          else:
            if archivo != None and nombreEqui=="":
              filename = secure_filename(archivo.filename)
              archivo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
              dir = os.listdir("./temp/")
              list = open("./temp/"+dir[0],"r")
              Equi = "Equipos encontrados:\n"
              for x in list:
                res = subprocess.Popen('cd ./historico/ && find "'+str(x)+'" ./*.txt', shell=True,stdout=subprocess.PIPE)
                out = res.stdout.read()
                if 'n1' in str(out):
                  nombre += "1"+str(out).split('n1')[1]
                  n = 1
                  while True:
                    if nombre[n]=="\\":
                      break
                    n+=1
                  nombre=nombre[:n]
                Equi += nombre + "\n"
              if Equi == "Equipos encontrados:\n":
                Equi = "No se encontro ningun equipo"
              os.remove("./temp/"+dir[0])
          listaD = listar()
          return render_template('index.html', opcion = listaD, nameEqui = Equi)
        else:
          if request.method=="POST" and 'botonCon' in request.form:
            ip = request.form.get("archivo")
            if ip !="":
              file = open(".\historico\\"+str(ip)+".txt","r")
              contenido = "IP;Hostname\n"
              for x in file:
                nombre = x.split(": ")[0]
                direccion = x.split(": ")[1]
                contenido += nombre + ";"+direccion
              listaD = listar()
              return render_template('index.html', opcion = listaD, archivo = str(ip), contenido = contenido)
            else:
              mensaje = "No hay archivos a convertir"
              listaD = listar()
              return render_template('index.html',opcion = listaD, mensaje = mensaje)
@app.route('/')
def index():  
  listaD = listar()
  return render_template('index.html', opcion = listaD)

def listar():
  dir = os.listdir("./historico/")
  listaD = []
  for x in dir:
    if str(x)!=".gitignore":
      listaD.append(str(x)[:-4])
  return listaD

if __name__ == "__main__":
  app.run()