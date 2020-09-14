import requests, htmlmin, time, sys

NEWGROUNDS_URL = "https://www.newgrounds.com/audio/listen/"

MAX_LENGTH_MIN = 3
MIN_LENGTH_MIN = 1
# MAX_LENGTH_SEC = 30
# MIN_LENGTH_SEC = 20

log_accepted = open("aceptadas.txt","a+")
log_rejected = open("rechazadas.txt","a+")
log_notfound = open("eliminadas.txt","a+")
accepted_counter = 0
rejected_counter = 0
notfound_counter = 0

#proxies_working = open("proxiesFuncionan.txt","a+")
#proxies_file = open("proxies.txt","r")
#proxies_list = proxies_file.readlines()
#proxy_index = 0
#proxy_length = len(proxies_list)

MAX_SLEEP_SECONDS = 600
sleeped_seconds = 0
times_sleeped = 0
last_id_slept = 0

"""
def setupProxy():
   ip = None
   try:
      ip = proxies_list[proxy_index].replace("\n","")
      ipNoPort = ip.split(":")[0]

      proxies = {'http': 'http://'+ip}
      req = requests.get('http://icanhazip.com/', timeout=6, proxies=proxies)
      data = req.text

      if(data.find(ipNoPort) >= 0):
         print "[{}] IP coincide".format(ip)
         return proxies
      else:
         print "[{}] IP no coincide, siguiente".format(ip)
         return None
   except requests.exceptions.RequestException, e:
      print "[{}] Error, siguiente".format(ip)
      return None
"""

def closeLogFiles():
   log_accepted.close()
   log_rejected.close()
   log_notfound.close()
   #proxies_file.close()

def log(logfile, info):
   logfile.write(info+"\n")

def isWithinRange(duration):
   minutes = duration[0]
   if(minutes > MAX_LENGTH_MIN or minutes < MIN_LENGTH_MIN):
      return False
      
   # seconds = duration[1]
   # if(seconds > MAX_LENGTH_SEC or seconds < MIN_LENGTH_SEC):
   #    return False
   return True

def getAudioDuration(songID):
   #Get Newgrounds shit, throws exception if song not found (idk why getHTTPCode doesnt work ffs)
   webUrl = None
   try:
      webUrl = requests.get(NEWGROUNDS_URL+str(songID), timeout=6)
   except Exception, e:
      print "[{}] Error de conexion a la pagina.".format(songID)
      print "  "+str(e)
      raise requests.exceptions.HTTPError('Error conexion')

   #Get Audio Duration
   webdata = htmlmin.minify(webUrl.text, remove_empty_space=True)
   if(webdata.find("You're making too many requests.") != -1):
      raise requests.exceptions.HTTPError('Too many requests')
   if(webdata.find("ERROR &mdash;") == -1):
      strDuration = webdata.split("<dt>File Info</dt>")[1].split("</dd>",3)[2].replace("<dd> ","")
      minutes = 0
      seconds = 0

      if(strDuration.find(" min")>=0):
         seconds = int(strDuration.split("min ")[1].split(" sec")[0])
         minutes = int(strDuration.split(" min")[0])
         pass
      else:
         seconds = int(strDuration.split(" sec")[0])
      return [minutes,seconds]
   else:
      return None

if __name__ == "__main__":

   #get args
   min_id = 0
   max_id = 605000 #cantidad hardcodeada pq me interesan las que vienen antes de esta id

   try:
      if(len(sys.argv) >= 2):
         min_id = int(sys.argv[1])
         if(len(sys.argv) >= 3):
            max_id = int(sys.argv[2])
   except Exception, e:
      print "Debes escribir un numero valido la concha de tu hermana"
      print "Uso correcto: python newgrounds.py <min-id> <max-id>"
      print str(e)
      exit()

   start = time.time()
   for id in xrange(min_id,max_id):

      """
      #set proxy
      proxies = None
      iteraciones = 0
      bol = True
      while(bol):
         if(proxy_index > proxy_length):
            proxy_index = 0
         for x in xrange(proxy_index,proxy_length):
            proxies = setupProxy()
            proxy_index+=1
            iteraciones+=1
            if(proxies is None and iteraciones >= 20):
               iteraciones=0
               print "Pausado por 5 minutos..."
               time.sleep(60*5)
            elif (proxies is not None):
               bol = False
               break
      """

      #gather info then process

      repeat = True
      while(repeat):
         try:
            duration = getAudioDuration(id)
            if(duration is not None):
               if(isWithinRange(duration)):
                  log(log_accepted,str(id))
                  print "{} ({}:{}) - Aceptado (Cancion dura entre 1m >=< 3m) [{}%]".format(str(id), str(duration[0]), str(duration[1]), str((id*100)/605000))
                  accepted_counter+=1
                  pass
               else:
                  print "{} ({}:{}) - Rechazado (Cancion no dura o excede de 1m >=< 3m) [{}%]".format(str(id), str(duration[0]), str(duration[1]), str((id*100)/605000))
                  log(log_rejected,str(id))
                  rejected_counter+=1
                  pass
               pass
            else:
               print "{} - Error (ahora inexistente) [{}%]".format(str(id), str((id*100)/605000) )
               log(log_notfound,str(id))
               notfound_counter+=1
            repeat = False
         except requests.exceptions.HTTPError, e:
            repeat = True

            times_sleeped+=1

            #una formula que me saque del culo LOL, pero proviene de como sacar porcentajes
            #((progreso*100)/maximo), pero quiero restarle el % al tiempo maximo de sleep
            seconds = MAX_SLEEP_SECONDS*(last_id_slept/id)
            
            if(seconds > 600):
               seconds = 600
            if(seconds < 60):
               seconds = 60

            last_id_slept=id
            sleeped_seconds+=seconds

            print "{} - Bloque de Newgrounds, esperare {} minutos".format(str(id), (seconds/60))
            print "  "+str(e)
            time.sleep(seconds)

   end = time.time()

   print "Terminado. ({} minutos, {} veces esperado)".format(((end-start)/60), times_sleeped)
   print " Estadisticas sobre la musica en NW:"
   print " Aceptadas (dentro de filtro): {}".format(str(accepted_counter))
   print " Rechazadas: {}".format(str(rejected_counter))
   print " Eliminadas o inexistentes: {}".format(str(notfound_counter))
   
   closeLogFiles()