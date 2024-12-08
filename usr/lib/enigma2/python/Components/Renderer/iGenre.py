#!/usr/bin/python
# -*- coding: utf-8 -*-

# edit lululla to 30.07.2022
# channelselections
# <widget render="irGenre" source="ServiceEvent" position="793,703" size="300,438" zPosition="3" transparent="1" />
# infobar
# <widget render="irGenre" source="session.Event_Now" position="54,315" size="300,438" zPosition="22" transparent="1" />
# <widget render="irGenre" source="session.Event_Next" position="54,429" size="300,438" zPosition="22" transparent="1" />
# recode from lululla 2023
from __future__ import print_function
from Components.Renderer.Renderer import Renderer
from Components.Sources.ServiceEvent import ServiceEvent
from Components.config import config
from six import text_type
from enigma import (
    ePixmap,
    loadPNG,
)
import re
import json
import os
import sys
import socket

from re import search, sub, I, S, escape
PY3 = False
if sys.version_info[0] >= 3:
    PY3 = True
    from urllib.request import urlopen
    from urllib.parse import quote_plus
    from urllib.error import HTTPError, URLError
else:
    from urllib2 import urlopen
    from urllib import quote_plus
    from urllib2 import HTTPError, URLError


try:
    from urllib import unquote, quote
except ImportError:
    from urllib.parse import unquote, quote


def isMountReadonly(mnt):
    mount_point = ''
    with open('/proc/mounts') as f:
        for line in f:
            line = line.split(',')[0]
            line = line.split()
            print('line ', line)
            try:
                device, mount_point, filesystem, flags = line
            except Exception as err:
                print("Error: %s" % err)
            if mount_point == mnt:
                return 'ro' in flags
    return "mount: '%s' doesn't exist" % mnt


def isMountedInRW(path):
    testfile = path + '/tmp-rw-test'
    os.system('touch ' + testfile)
    if os.path.exists(testfile):
        os.system('rm -f ' + testfile)
        return True
    return False


curskin = config.skin.primary_skin.value.replace('/skin.xml', '')
PIC_PATH = '/usr/share/enigma2/%s/genre_pic/' % curskin
found = False
path_folder = "/tmp/poster"
if os.path.exists("/media/hdd"):
    if isMountedInRW("/media/hdd"):
        path_folder = "/media/hdd/poster"
elif os.path.exists("/media/usb"):
    if isMountedInRW("/media/usb"):
        path_folder = "/media/usb/poster"
elif os.path.exists("/media/mmc"):
    if isMountedInRW("/media/mmc"):
        path_folder = "/media/mmc/poster"

if not os.path.exists(path_folder):
    os.makedirs(path_folder)


def OnclearMem():
    try:
        os.system('sync')
        os.system('echo 1 > /proc/sys/vm/drop_caches')
        os.system('echo 2 > /proc/sys/vm/drop_caches')
        os.system('echo 3 > /proc/sys/vm/drop_caches')
    except:
        pass


def quoteEventName(eventName):
    try:
        text = eventName.decode('utf8').replace(u'\x86', u'').replace(u'\x87', u'').encode('utf8')
    except:
        text = eventName
    return quote_plus(text, safe="+")


REGEX = re.compile(
    r'[\(\[].*?[\)\]]|'                    # Parentesi tonde o quadre
    r':?\s?odc\.\d+|'                      # odc. con o senza numero prima
    r'\d+\s?:?\s?odc\.\d+|'                # numero con odc.
    r'[:!]|'                               # due punti o punto esclamativo
    r'\s-\s.*|'                            # trattino con testo successivo
    r',|'                                  # virgola
    r'/.*|'                                # tutto dopo uno slash
    r'\|\s?\d+\+|'                         # | seguito da numero e +
    r'\d+\+|'                              # numero seguito da +
    r'\s\*\d{4}\Z|'                        # * seguito da un anno a 4 cifre
    r'[\(\[\|].*?[\)\]\|]|'                # Parentesi tonde, quadre o pipe
    r'(?:\"[\.|\,]?\s.*|\"|'               # Testo tra virgolette
    r'\.\s.+)|'                            # Punto seguito da testo
    r'Премьера\.\s|'                       # Specifico per il russo
    r'[хмтдХМТД]/[фс]\s|'                  # Pattern per il russo con /ф o /с
    r'\s[сС](?:езон|ерия|-н|-я)\s.*|'      # Stagione o episodio in russo
    r'\s\d{1,3}\s[чсЧС]\.?\s.*|'           # numero di parte/episodio in russo
    r'\.\s\d{1,3}\s[чсЧС]\.?\s.*|'         # numero di parte/episodio in russo con punto
    r'\s[чсЧС]\.?\s\d{1,3}.*|'             # Parte/Episodio in russo
    r'\d{1,3}-(?:я|й)\s?с-н.*',            # Finale con numero e suffisso russo
    re.DOTALL)


def intCheck():
    try:
        response = urlopen("http://google.com", None, 5)
        response.close()
    except HTTPError:
        return False
    except URLError:
        return False
    except socket.timeout:
        return False
    return True


def remove_accents(string):
    if not isinstance(string, text_type):
        string = text_type(string, 'utf-8')
    string = sub(u"[àáâãäå]", 'a', string)
    string = sub(u"[èéêë]", 'e', string)
    string = sub(u"[ìíîï]", 'i', string)
    string = sub(u"[òóôõö]", 'o', string)
    string = sub(u"[ùúûü]", 'u', string)
    string = sub(u"[ýÿ]", 'y', string)
    return string


def unicodify(s, encoding='utf-8', norm=None):
    if not isinstance(s, text_type):
        s = text_type(s, encoding)
    if norm:
        from unicodedata import normalize
        s = normalize(norm, s)
    return s


def str_encode(text, encoding="utf8"):
    if not PY3:
        if isinstance(text, text_type):
            return text.encode(encoding)
    return text


def cutName(eventName=""):
    if eventName:
        eventName = eventName.replace('"', '').replace('.', '').replace(' | ', '')  # .replace('Х/Ф', '').replace('М/Ф', '').replace('Х/ф', '')
        eventName = eventName.replace('(18+)', '').replace('18+', '').replace('(16+)', '').replace('16+', '').replace('(12+)', '')
        eventName = eventName.replace('12+', '').replace('(7+)', '').replace('7+', '').replace('(6+)', '').replace('6+', '')
        eventName = eventName.replace('(0+)', '').replace('0+', '').replace('+', '')
        eventName = eventName.replace('المسلسل العربي', '')
        eventName = eventName.replace('مسلسل', '')
        eventName = eventName.replace('برنامج', '')
        eventName = eventName.replace('فيلم وثائقى', '')
        eventName = eventName.replace('حفل', '')
        return eventName
    return ""


def getCleanTitle(eventitle=""):
    # save_name = sub('\\(\d+\)$', '', eventitle)
    # save_name = sub('\\(\d+\/\d+\)$', '', save_name)  # remove episode-number " (xx/xx)" at the end
    # # save_name = sub('\ |\?|\.|\,|\!|\/|\;|\:|\@|\&|\'|\-|\"|\%|\(|\)|\[|\]\#|\+', '', save_name)
    save_name = eventitle.replace(' ^`^s', '').replace(' ^`^y', '')
    return save_name


def dataenc(data):
    if PY3:
        data = data.decode("utf-8")
    else:
        data = data.encode("utf-8")
    return data


def sanitize_filename(filename):
    # Replace spaces with underscores and remove invalid characters (like ':')
    sanitized = sub(r'[^\w\s-]', '', filename)  # Remove invalid characters
    # sanitized = sanitized.replace(' ', '_')      # Replace spaces with underscores
    # sanitized = sanitized.replace('-', '_')      # Replace dashes with underscores
    return sanitized.strip()


def convtext(text=''):
        if text is None:
            print('return None original text:', type(text))
            return  # Esci dalla funzione se text è None
        if text == '':
            print('text is an empty string')
        else:
            print('original text:' + text)
            text = text.lower()
            print('lowercased text:' + text)
            text = text.lstrip()
            # text = cutName(text)
            # text = getCleanTitle(text)
            if text.endswith("the"):
                text = "the " + text[:-4]
            # Modifiche personalizzate
            if 'giochi olimpici parigi' in text:
                text = 'olimpiadi di parigi'
            if 'bruno barbieri' in text:
                text = text.replace('bruno barbieri', 'brunobarbierix')
            if "anni '60" in text:
                text = "anni 60"
            if 'tg regione' in text:
                text = 'tg3'
            if 'studio aperto' in text:
                text = 'studio aperto'
            if 'josephine ange gardien' in text:
                text = 'josephine ange gardien'
            if 'elementary' in text:
                text = 'elementary'
            if 'squadra speciale cobra 11' in text:
                text = 'squadra speciale cobra 11'
            if 'criminal minds' in text:
                text = 'criminal minds'
            if 'i delitti del barlume' in text:
                text = 'i delitti del barlume'
            if 'senza traccia' in text:
                text = 'senza traccia'
            if 'hudson e rex' in text:
                text = 'hudson e rex'
            if 'ben-hur' in text:
                text = 'ben-hur'
            if 'alessandro borghese - 4 ristoranti' in text:
                text = 'alessandroborgheseristoranti'
            if 'alessandro borghese: 4 ristoranti' in text:
                text = 'alessandroborgheseristoranti'
            cutlist = ['x264', '720p', '1080p', '1080i', 'pal', 'german', 'english', 'ws', 'dvdrip', 'unrated',
                       'retail', 'web-dl', 'dl', 'ld', 'mic', 'md', 'dvdr', 'bdrip', 'bluray', 'dts', 'uncut', 'anime',
                       'ac3md', 'ac3', 'ac3d', 'ts', 'dvdscr', 'complete', 'internal', 'dtsd', 'xvid', 'divx', 'dubbed',
                       'line.dubbed', 'dd51', 'dvdr9', 'dvdr5', 'h264', 'avc', 'webhdtvrip', 'webhdrip', 'webrip',
                       'webhdtv', 'webhd', 'hdtvrip', 'hdrip', 'hdtv', 'ituneshd', 'repack', 'sync', '1^tv', '1^ tv',
                       '1^ visione rai', '1^ visione', ' - prima tv', ' - primatv', 'prima visione',
                       'film -', 'de filippi', 'first screening',
                       'live:', 'new:', 'film:', 'première diffusion', 'nouveau:', 'en direct:',
                       'premiere:', 'estreno:', 'nueva emisión:', 'en vivo:'
                       ]
            for word in cutlist:
                text = text.replace(word, '')
            text = ' '.join(text.split())
            print(text)
            text = cutName(text)
            text = getCleanTitle(text)

            text = text.partition("-")[0]  # Mantieni solo il testo prima del primo "-"
            # Pulizia finale
            text = text.replace('.', ' ').replace('-', ' ').replace('_', ' ').replace('+', '')

            # Rimozione pattern specifici
            if search(r'[Ss][0-9]+[Ee][0-9]+', text):
                text = sub(r'[Ss][0-9]+[Ee][0-9]+.*[a-zA-Z0-9_]+', '', text, flags=S | I)
            text = sub(r'\(.*\)', '', text).rstrip()
            text = text.partition("(")[0]
            text = sub(r"\\s\d+", "", text)
            text = text.partition(":")[0]
            text = sub(r'(odc.\s\d+)+.*?FIN', '', text)
            text = sub(r'(odc.\d+)+.*?FIN', '', text)
            text = sub(r'(\d+)+.*?FIN', '', text)
            text = sub('FIN', '', text)
            # remove episode number in arabic series
            text = sub(r'\sح\s*\d+', '', text)
            # remove season number in arabic series
            text = sub(r'\sج\s*\d+', '', text)
            # remove season number in arabic series
            text = sub(r'\sم\s*\d+', '', text)
            # Forzature finali
            text = text.replace('XXXXXX', '60')
            text = text.replace('brunobarbierix', 'bruno barbieri - 4 hotel')
            text = text.replace('alessandroborgheseristoranti', 'alessandro borghese - 4 ristoranti')
            text = text.replace('il ritorno di colombo', 'colombo')
            text = quote(text, safe="")
            print('text final: ', text)
        return unquote(text).capitalize()


class irGenre(Renderer):

    def __init__(self):
        Renderer.__init__(self)

    GUI_WIDGET = ePixmap

    def changed(self, what):
        if not self.instance:
            return
        if what[0] != self.CHANGED_CLEAR:
            if self.instance:
                self.instance.hide()
            self.delay()

    def delay(self):
        global found
        self.pstrNm = ''
        genreTxt = None
        self.event = self.source.event
        if not self.event:
            return
        if self.event and self.event != 'None' or self.event is not None:
            try:
                if PY3:
                    self.evnt = self.event.getEventName().replace('\xc2\x86', '').replace('\xc2\x87', '')  # .encode('utf-8')
                else:
                    self.evnt = self.event.getEventName().replace('\xc2\x86', '').replace('\xc2\x87', '').encode('utf-8')
                self.evntNm = convtext(self.evnt)
                infos_file = "{}/{}".format(path_folder, self.evntNm)
                if os.path.exists(infos_file):
                    with open(infos_file) as f:
                        genreTxt = json.load(f)['Genre']
                        genreTxt = genreTxt.split(",")[0]
                        print('genreTxt name: ', genreTxt)
                if genreTxt is not None:
                    try:

                        gData = self.event.getGenreData()
                        if gData:
                            genreTxt = {
                                1: ('N/A', 'Action', 'Thriller', 'Drama', 'Movie', 'Detective', 'Mistery', 'Adventure', 'Science', 'Animation', 'Comedy', 'Serie', 'Romance', 'Serious', 'Adult'),
                                2: ('News', 'Weather', 'Magazine', 'Docu', 'Disc', 'Documetary'),
                                3: ('Show', 'Quiz', 'Variety', 'Talk'),
                                4: ('Sports', 'Special', 'Sports Magazine', 'Football', 'Tennis', 'Team Sports', 'Athletics', 'Motor Sport', 'Water Sport', 'Winter Sport', 'Equestrian', 'Martial Sports'),
                                5: ("Childrens", "Children", 'entertainment (6-14)', 'entertainment (10-16)', 'Information', 'Cartoon'),
                                6: ('Music', 'Rock/Pop', 'Classic Music', 'Folk', 'Jazz', 'Musical/Opera', 'Ballet'),
                                7: ('Arts', 'Performing Arts', 'Fine Arts', 'Religion', 'PopCulture', 'Literature', 'Cinema', 'ExpFilm', 'Press', 'New Media', 'Culture', 'Fashion'),
                                8: ('Social', 'Magazines', 'Economics', 'Remarkable People'),
                                9: ('Education', 'Nature/Animals/', 'Technology', 'Medicine', 'Expeditions', 'Social', 'Further Education', 'Languages'),
                                10: ('Hobbies', 'Travel', 'Handicraft', 'Motoring', 'Fitness', 'Cooking', 'Shopping', 'Gardening'),
                                11: ('Original Language', 'Black & White', 'Unpublished', 'Live Broadcast'),
                                12: ('Adventure'),
                                14: ('Fantasy'),
                                16: ('Animation'),
                                18: ('Drama'),
                                27: ('Horror', 'Thriller'),
                                28: ('Action'),
                                35: ('Comedy'),
                                36: ('History'),
                                37: ('Western'),
                                53: ('Thriller', 'Horror'),
                                80: ('Crime'),
                                99: ('Documentary'),
                                878: ('Science Fiction', 'Science', 'Fiction'),
                                9648: ('Mystery'),
                                10402: ('Music'),
                                10751: ('Family'),
                                10752: ('War'),
                                10759: ('Action & Adventure', 'Action', 'Adventure'),
                                10762: ('Kids'),
                                10763: ('News'),
                                10764: ('Reality'),
                                10765: ('Sci-Fi & Fantasy', 'Sci-Fi', 'Fantasy'),
                                10766: ('Soap'),
                                10767: ('Talk'),
                                10768: ('War & Politics '),
                                10770: ('TV Movie')}.get(gData.getLevel1(), "")[gData.getLevel2()]
                    except:
                        pass
                print('Genre Txt 11 : ', genreTxt)
                png = "%s%s.png" % (PIC_PATH, sub("[^0-9a-z]+", "_", genreTxt.lower()).replace("__", "_").strip("_"))
                if os.path.exists(png):
                    found = True
                    print('PNG name: ', png)
                    if not PY3:
                        png = png.encode()
                    self.instance.setPixmap(loadPNG(png))
                    self.instance.setScale(1)
                    self.instance.show()
                if not found:
                    try:
                        print('No Found Genre : ', found)
                        return genreTxt
                    except:
                        print('except No Found GenreTxt: ')
                        if self.instance:
                            self.instance.hide()
            except Exception as e:
                print('irGenre error get event: ',  str(e))
                pass
