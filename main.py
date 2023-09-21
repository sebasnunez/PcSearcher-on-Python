from flask import Flask, render_template, request
import os
import wget
app = Flask(__name__)

import subprocess
@app.route("/", methods = ["POST"])
def recorrerIp():
  if request.method=="POST" and 'recorrer' in request.form:
    ip = request.form.get("ip")
    file = open("./historico/ips/"+str(ip)+".txt", "w")
    for i in range(253):
      res = subprocess.Popen("ping -n 1 " + str(ip)+"."+str(i+2), shell=True, stdout=subprocess.PIPE)
      out = res.stdout.read()
      if str(out)[-6]=="s":
        file.write(str(ip)+"."+str(i+2)+"\n")
      print(str(ip)+"."+str(i+2)) 
    file.close()
    file2 = open("./historico/ips/"+ip+".txt", "r")
    ls = []
    for x in file2:
      ls.append(x)
    file2.close()
    listaD = listar()
    return render_template("index.html",list = ls, opcion = listaD)
  else:
    if request.method=="POST" and 'nombres' in request.form:
      ipB = request.form.get("ipB")
      print(str(ipB))
      file = open("./historico/ips/"+str(ipB)+".txt", "r")
      file2 = open("./historico/hostnames/"+str(ipB)+".txt", "w")
      for i in file:
        ip = i
        res = subprocess.Popen("CD .\PSTools && PsExec \\\\"+str(ip[:-1])+" hostname", shell=True,stdout=subprocess.PIPE)
        out = res.stdout.read()
        final = ""
        if str(out)[-18]=="r":
          print("Error de Conexion")
        else:
          for j in range(13):
            final += str(out)[-18+j]
          file2.write(str(ip[:-1])+": "+final+"\n")
      file.close()  
      file2.close()
      file3 = open("./historico/hostnames/"+str(ipB)+".txt", "r")
      ls = []
      for x in file3:
        ls.append(x)
      file3.close()
      listaD = listar()
      return render_template("index.html",names = ls, opcion = listaD)
    else:
      if request.method=="POST" and 'historicoRecorrido' in request.form:
        des = request.form.get("des")
        file = open("./historico/ips/"+str(des) + ".txt", "r")
        ls1 = []
        for x in file:
          ls1.append(x)
        file.close()
        ls2 = []
        if os.path.isfile("./historico/hostnames/"+str(des)+".txt"):
          file = open("./historico/hostnames/"+str(des)+".txt", "r")
          for x in file:
            ls2.append(x)
          file.close()
        listaD = listar()
        return render_template("index.html",names = ls2, list = ls1, opcion = listaD)
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
            res = subprocess.Popen('cd ./historico/hostnames/ && find "'+str(nombreEqui)+'" ./*.txt', shell=True,stdout=subprocess.PIPE)
            out = res.stdout.read()
            if 'n1' in str(out):
              nombre="1"+str(out).split('n1')[1]
              n = 1
              while True:
                if nombre[n]=="\\":
                  break
                n+=1
              nombre=nombre[:n]
            else:
              nombre = 'El equipo no se encuentra en ninguna consulta'
            listaD = listar()
            return render_template('index.html', opcion = listaD, nameEqui = nombre)
          else:
            if request.method=="POST" and 'botonCon' in request.form:
              ip = request.form.get("archivo")
              file = open(".\historico\hostnames\\"+str(ip)+".txt","r")
              contenido = "Hostname;IP \n"
              for x in file:
                nombre = x.split(": ")[0]
                direccion = x.split(": ")[1]
                contenido += nombre + ";"+direccion
              temp = open("./temp.csv", "w")
              temp.write(contenido)
              temp.close()
              listaD = listar()
              return render_template('index.html', opcion = listaD, archivo = str(ip), contenido = contenido)
@app.route('/')
def index():
  listaD = listar()
  return render_template('index.html', opcion = listaD)

def listar():
  dir = os.listdir("./historico/ips")
  listaD = []
  for x in dir:
    if str(x)!=".gitignore":
      listaD.append(str(x)[:-4])
  return listaD

if __name__ == "__main__":
  app.run()