# -*- coding: utf-8 -*- 

import sys
import os
import re
import xmlrpclib
import unicodedata
import struct
from xml.dom import minidom
import urllib, zlib
import xbmc, xbmcvfs
import lxml
from lxml.html.clean import Cleaner
import requests
from BeautifulSoup import BeautifulSoup

try:
  # Python 2.6 +
  from hashlib import md5 as md5
  from hashlib import sha256
except ImportError:
  # Python 2.5 and earlier
  from md5 import md5
  from sha256 import sha256
  
__addon__      = sys.modules[ "__main__" ].__addon__
__scriptname__ = sys.modules[ "__main__" ].__scriptname__
__version__    = sys.modules[ "__main__" ].__version__
__cwd__        = sys.modules[ "__main__" ].__cwd__
__language__   = sys.modules[ "__main__" ].__language__
__scriptid__   = sys.modules[ "__main__" ].__scriptid__

USER_AGENT        = "%s_v%s" % (__scriptname__.replace(" ","_"),__version__ )
REQUEST_HEADERS   = {'Accept-Language': 'es-419,es;q=0.8,ar;q=0.6,en;q=0.4,gl;q=0.2,de;q=0.2,pt;q=0.2',}
HOST              = "https://www.podnapisi.net"
SEARCH_URL        = HOST + "/ppodnapisi/search?tbsl=1&sK=%s&sJ=%s&sY=%s&sTS=%s&sTE=%s&sXML=1&lang=0"
SEARCH_URL        = HOST + "/subtitles/search/?keywords=%s&movie_type=%s&year=%s&seasons=%s&episodes=%s&language=%s"
SEARCH_URL_HASH   = HOST + "/ppodnapisi/search?tbsl=1&sK=%s&sJ=%s&sY=%s&sTS=%s&sTE=%s&sMH=%s&sXML=1&lang=0"

DOWNLOAD_URL      = "http://www.podnapisi.net/subtitles/%s/download"

LANGUAGES      = (

    # Full Language name[0]     podnapisi[1]  ISO 639-1[2]   ISO 639-1 Code[3]   Script Setting Language[4]   localized name id number[5]

    ("Albanian"                   , "29",       "sq",            "alb",                 "0",                     30201  ),
    ("Arabic"                     , "12",       "ar",            "ara",                 "1",                     30202  ),
    ("Belarusian"                 , "0" ,       "hy",            "arm",                 "2",                     30203  ),
    ("Bosnian"                    , "10",       "bs",            "bos",                 "3",                     30204  ),
    ("Bulgarian"                  , "33",       "bg",            "bul",                 "4",                     30205  ),
    ("Catalan"                    , "53",       "ca",            "cat",                 "5",                     30206  ),
    ("Chinese"                    , "17",       "zh",            "chi",                 "6",                     30207  ),
    ("Croatian"                   , "38",       "hr",            "hrv",                 "7",                     30208  ),
    ("Czech"                      , "7",        "cs",            "cze",                 "8",                     30209  ),
    ("Danish"                     , "24",       "da",            "dan",                 "9",                     30210  ),
    ("Dutch"                      , "23",       "nl",            "dut",                 "10",                    30211  ),
    ("English"                    , "2",        "en",            "eng",                 "11",                    30212  ),
    ("Estonian"                   , "20",       "et",            "est",                 "12",                    30213  ),
    ("Persian"                    , "52",       "fa",            "per",                 "13",                    30247  ),
    ("Finnish"                    , "31",       "fi",            "fin",                 "14",                    30214  ),
    ("French"                     , "8",        "fr",            "fre",                 "15",                    30215  ),
    ("German"                     , "5",        "de",            "ger",                 "16",                    30216  ),
    ("Greek"                      , "16",       "el",            "ell",                 "17",                    30217  ),
    ("Hebrew"                     , "22",       "he",            "heb",                 "18",                    30218  ),
    ("Hindi"                      , "42",       "hi",            "hin",                 "19",                    30219  ),
    ("Hungarian"                  , "15",       "hu",            "hun",                 "20",                    30220  ),
    ("Icelandic"                  , "6",        "is",            "ice",                 "21",                    30221  ),
    ("Indonesian"                 , "0",        "id",            "ind",                 "22",                    30222  ),
    ("Italian"                    , "9",        "it",            "ita",                 "23",                    30224  ),
    ("Japanese"                   , "11",       "ja",            "jpn",                 "24",                    30225  ),
    ("Korean"                     , "4",        "ko",            "kor",                 "25",                    30226  ),
    ("Latvian"                    , "21",       "lv",            "lav",                 "26",                    30227  ),
    ("Lithuanian"                 , "0",        "lt",            "lit",                 "27",                    30228  ),
    ("Macedonian"                 , "35",       "mk",            "mac",                 "28",                    30229  ),
    ("Malay"                      , "0",        "ms",            "may",                 "29",                    30248  ),    
    ("Norwegian"                  , "3",        "no",            "nor",                 "30",                    30230  ),
    ("Polish"                     , "26",       "pl",            "pol",                 "31",                    30232  ),
    ("Portuguese"                 , "32",       "pt",            "por",                 "32",                    30233  ),
    ("PortugueseBrazil"           , "48",       "pb",            "pob",                 "33",                    30234  ),
    ("Romanian"                   , "13",       "ro",            "rum",                 "34",                    30235  ),
    ("Russian"                    , "27",       "ru",            "rus",                 "35",                    30236  ),
    ("Serbian"                    , "36",       "sr",            "scc",                 "36",                    30237  ),
    ("Slovak"                     , "37",       "sk",            "slo",                 "37",                    30238  ),
    ("Slovenian"                  , "1",        "sl",            "slv",                 "38",                    30239  ),
    ("Spanish"                    , "28",       "es",            "spa",                 "39",                    30240  ),
    ("Swedish"                    , "25",       "sv",            "swe",                 "40",                    30242  ),
    ("Thai"                       , "0",        "th",            "tha",                 "41",                    30243  ),
    ("Turkish"                    , "30",       "tr",            "tur",                 "42",                    30244  ),
    ("Ukrainian"                  , "46",       "uk",            "ukr",                 "43",                    30245  ),
    ("Vietnamese"                 , "51",       "vi",            "vie",                 "44",                    30246  ),
    ("BosnianLatin"               , "10",       "bs",            "bos",                 "100",                   30204  ),
    ("Farsi"                      , "52",       "fa",            "per",                 "13",                    30247  ),
    ("English (US)"               , "2",        "en",            "eng",                 "100",                   30212  ),
    ("English (UK)"               , "2",        "en",            "eng",                 "100",                   30212  ),
    ("Portuguese (Brazilian)"     , "48",       "pt-br",         "pob",                 "100",                   30234  ),
    ("Portuguese (Brazil)"        , "48",       "pb",            "pob",                 "33",                    30234  ),
    ("Portuguese-BR"              , "48",       "pb",            "pob",                 "33",                    30234  ),
    ("Brazilian"                  , "48",       "pb",            "pob",                 "33",                    30234  ),
    ("Español (Latinoamérica)"    , "28",       "es",            "spa",                 "100",                   30240  ),
    ("Español (España)"           , "28",       "es",            "spa",                 "100",                   30240  ),
    ("Spanish (Latin America)"    , "28",       "es",            "spa",                 "100",                   30240  ),
    ("Español"                    , "28",       "es",            "spa",                 "100",                   30240  ),
    ("SerbianLatin"               , "36",       "sr",            "scc",                 "100",                   30237  ),
    ("Spanish (Spain)"            , "28",       "es",            "spa",                 "100",                   30240  ),
    ("Chinese (Traditional)"      , "17",       "zh",            "chi",                 "100",                   30207  ),
    ("Chinese (Simplified)"       , "17",       "zh",            "chi",                 "100",                   30207  ) )


def languageTranslate(lang, lang_from, lang_to):
  for x in LANGUAGES:
    if lang == x[lang_from] :
      return x[lang_to]

def getLanguageName(lang):
  for language in LANGUAGES:
    if lang == language[2] :
      return language[0]

def log(module, msg):
  xbmc.log((u"### [%s] - %s" % (module,msg,)).encode('utf-8'),level=xbmc.LOGDEBUG ) 

def normalizeString(str):
  return unicodedata.normalize(
         'NFKD', unicode(unicode(str, 'utf-8'))
         ).encode('ascii','ignore')

def OpensubtitlesHash(item):
    try:
      if item["rar"]:
        return OpensubtitlesHashRar(item['file_original_path'])
        
      log( __scriptid__,"Hash Standard file")  
      longlongformat = 'q'  # long long
      bytesize = struct.calcsize(longlongformat)
      
      f = xbmcvfs.File(item['file_original_path'])
      filesize = f.size()
      hash = filesize
      
      if filesize < 65536 * 2:
          return "SizeError"
      
      buffer = f.read(65536)
      f.seek(max(0,filesize-65536),0)
      buffer += f.read(65536)
      f.close()
      for x in range((65536/bytesize)*2):
          size = x*bytesize
          (l_value,)= struct.unpack(longlongformat, buffer[size:size+bytesize])
          hash += l_value
          hash = hash & 0xFFFFFFFFFFFFFFFF
      
      returnHash = "%016x" % hash
    except:
      returnHash = "000000000000"

    return returnHash

def OpensubtitlesHashRar(firstrarfile):
    log( __scriptid__,"Hash Rar file")
    f = xbmcvfs.File(firstrarfile)
    a=f.read(4)
    if a!='Rar!':
        raise Exception('ERROR: This is not rar file.')
    seek=0
    for i in range(4):
        f.seek(max(0,seek),0)
        a=f.read(100)        
        type,flag,size=struct.unpack( '<BHH', a[2:2+5]) 
        if 0x74==type:
            if 0x30!=struct.unpack( '<B', a[25:25+1])[0]:
                raise Exception('Bad compression method! Work only for "store".')            
            s_partiizebodystart=seek+size
            s_partiizebody,s_unpacksize=struct.unpack( '<II', a[7:7+2*4])
            if (flag & 0x0100):
                s_unpacksize=(struct.unpack( '<I', a[36:36+4])[0] <<32 )+s_unpacksize
                log( __name__ , 'Hash untested for files biger that 2gb. May work or may generate bad hash.')
            lastrarfile=getlastsplit(firstrarfile,(s_unpacksize-1)/s_partiizebody)
            hash=addfilehash(firstrarfile,s_unpacksize,s_partiizebodystart)
            hash=addfilehash(lastrarfile,hash,(s_unpacksize%s_partiizebody)+s_partiizebodystart-65536)
            f.close()
            return (s_unpacksize,"%016x" % hash )
        seek+=size
    raise Exception('ERROR: Not Body part in rar file.')

def dec2hex(n, l=0):
  # return the hexadecimal string representation of integer n
  s = "%X" % n
  if (l > 0) :
    while len(s) < l:
      s = "0" + s 
  return s

def invert(basestring):
  asal = [basestring[i:i+2]
          for i in range(0, len(basestring), 2)]
  asal.reverse()
  return ''.join(asal)

def calculateSublightHash(filename):

  DATA_SIZE = 128 * 1024;

  if not xbmcvfs.exists(filename) :
    return "000000000000"
  
  fileToHash = xbmcvfs.File(filename)

  if fileToHash.size(filename) < DATA_SIZE :
    return "000000000000"

  sum = 0
  hash = ""
  
  number = 2
  sum = sum + number
  hash = hash + dec2hex(number, 2) 
  
  filesize = fileToHash.size(filename)
  
  sum = sum + (filesize & 0xff) + ((filesize & 0xff00) >> 8) + ((filesize & 0xff0000) >> 16) + ((filesize & 0xff000000) >> 24)
  hash = hash + dec2hex(filesize, 12) 
  
  buffer = fileToHash.read( DATA_SIZE )
  begining = zlib.adler32(buffer) & 0xffffffff
  sum = sum + (begining & 0xff) + ((begining & 0xff00) >> 8) + ((begining & 0xff0000) >> 16) + ((begining & 0xff000000) >> 24)
  hash = hash + invert(dec2hex(begining, 8))

  fileToHash.seek(filesize/2,0)
  buffer = fileToHash.read( DATA_SIZE )
  middle = zlib.adler32(buffer) & 0xffffffff
  sum = sum + (middle & 0xff) + ((middle & 0xff00) >> 8) + ((middle & 0xff0000) >> 16) + ((middle & 0xff000000) >> 24)
  hash = hash + invert(dec2hex(middle, 8))

  fileToHash.seek(filesize-DATA_SIZE,0)
  buffer = fileToHash.read( DATA_SIZE )
  end = zlib.adler32(buffer) & 0xffffffff
  sum = sum + (end & 0xff) + ((end & 0xff00) >> 8) + ((end & 0xff0000) >> 16) + ((end & 0xff000000) >> 24)
  hash = hash + invert(dec2hex(end, 8))
  
  fileToHash.close()
  hash = hash + dec2hex(sum % 256, 2)
  
  return hash.lower()

class PNServer:
  def Create(self):
    self.subtitles_list = []
    self.connected = False
    
  def Login(self):
    self.podserver   = xmlrpclib.Server('http://ssp.podnapisi.net:8000')
    init        = self.podserver.initiate(USER_AGENT)  
    hash        = md5()
    hash.update(__addon__.getSetting( "PNpass" ))
    self.password = sha256(str(hash.hexdigest()) + str(init['nonce'])).hexdigest()
    self.user     = __addon__.getSetting( "PNuser" )
    if init['status'] == 200:
      self.pod_session = init['session']
      auth = self.podserver.authenticate(self.pod_session, self.user, self.password)
      if auth['status'] == 300: 
        log( __scriptid__ ,__language__(32005))
        xbmc.executebuiltin(u'Notification(%s,%s,5000,%s)' %(__scriptname__,
                                                             __language__(32005),
                                                             os.path.join(__cwd__,"icon.png")
                                                            )
                            )
        self.connected = False
      else:
        log( __scriptid__ ,"Connected to Podnapisi server")
        self.connected = True
    else:
      self.connected = False 

  def SearchSubtitlesWeb( self, item):
    if len(item['tvshow']) > 1:
      item['title'] = item['tvshow']
    
    if (__addon__.getSetting("PNmatch") == 'true'):
      url =  SEARCH_URL_HASH % (item['title'].replace(" ","+"),
                               ','.join(item['3let_language']),
                               str(item['year']),
                               str(item['season']), 
                               str(item['episode']),
                               '%s,sublight:%s,sublight:%s' % (item['OShash'],item['SLhash'],md5(item['SLhash']).hexdigest() )
                               )
    else:

      title, year = xbmc.getCleanMovieTitle(item['title'])
      lang = __addon__.getSetting("language")

      url =  SEARCH_URL % (title.replace(" ","+").replace(".","+"),
                           str(''),
                           str(year),
                           str(item['season']), 
                           str(item['episode']),
                           str(lang)
                          )

    log( __scriptid__ ,"Search URL - %s" % (url))
    
    subtitles = self.fetch(url)

    if subtitles:
      for subtitle in subtitles:
        title = self.get_element(subtitle, "release")

        if title == "":
          title = self.get_element(subtitle, "title")

          if title == "":
            title = "Without release"
        
        hashMatch = False
        if (item['OShash'] in self.get_element(subtitle, "exactHashes") or 
           item['SLhash'] in self.get_element(subtitle, "exactHashes")):
          hashMatch = True

        lang = self.get_element(subtitle, "language")

        self.subtitles_list.append({'filename'      : title,
                                    'link'          : subtitle["data-href"],
                                    'movie_id'      : self.get_element(subtitle, "movieId"),
                                    'season'        : self.get_element(subtitle, "tvSeason"),
                                    'episode'       : self.get_element(subtitle, "tvEpisode"),
                                    'language_name' : getLanguageName(lang),
                                    'language_flag' : lang,
                                    'rating'        : '0',
                                    'sync'          : hashMatch,
                                    'hearing_imp'   : "n" in self.get_element(subtitle, "flags")
                                    })
      self.mergesubtitles()
    return self.subtitles_list
  
  def Download(self,params):
    print params
    subtitle_ids = []
    if (__addon__.getSetting("PNmatch") == 'true' and params["hash"] != "000000000000"):
      self.Login()
      if params["match"] == "True":
        subtitle_ids.append(str(params["link"]))

      log( __scriptid__ ,"Sending match to Podnapisi server")
      result = self.podserver.match(self.pod_session, params["hash"], params["movie_id"], int(params["season"]), int(params["episode"]), subtitle_ids)
      if result['status'] == 200:
        log( __scriptid__ ,"Match successfuly sent")

    print HOST + str(params["link"])

    return HOST + str(params["link"]) + "/download"

  def get_element(self, element, tag):

    expression = r"\b%s\b" % (tag)

    bs_element = element.find(attrs={"class": re.compile(expression)})

    if bs_element:
      return bs_element.text
    else:
      return ""  

  def fetch(self, url):


    # The url automatically redirects if find an specific movie.
    # If the search matches more than one movie, there is no redirection
    # and reurns a list of movies.
    req = requests.get(url, headers=REQUEST_HEADERS, allow_redirects=False)
    req.encoding = 'ISO-8859-9'
    html = req.text.encode('ISO-8859-9')

    page = BeautifulSoup(html)

    # Checking if there is a movie list in the response
    if (self.bf_check_movie_list(page)):

      raw_subtitle_list = []
      movie_list = self.bf_get_movie_list(page)
      for movie in movie_list:
        raw_subtitle_list += self.fetch_page_single(HOST + movie['href'])

      return raw_subtitle_list
    else:
      return self.fetch_page_single(url)

  def bf_check_movie_list(self, page):
    return True if page.findAll(attrs={"class": re.compile(r'\bmovie_item\b')}) else False

  def bf_get_movie_list(self, page):
    return page.findAll(attrs={"class": re.compile(r'\bmovie_item\b')})

  def fetch_page_single(self, url):
    url += '&sort=stats.downloads&order=desc#list'
    print "SEARCH URL: " + url
    req = requests.get(url, headers=REQUEST_HEADERS)
    req.encoding = 'ISO-8859-9'
    html = req.text.encode('ISO-8859-9')

    page = BeautifulSoup(html)

    return page.findAll("tr", {"class": "subtitle-entry"})

  def compare_columns(self, b, a):
    return cmp( b["language_name"], a["language_name"] )  or cmp( a["sync"], b["sync"] ) 

  def mergesubtitles(self):
    if( len ( self.subtitles_list ) > 0 ):
      self.subtitles_list = sorted(self.subtitles_list, self.compare_columns)
       
