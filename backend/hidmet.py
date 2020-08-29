import re
import sys
import requests

EXIT_SUCCESS = 0
EXIT_NO_KNOWN_STATIONS = 11

HEADER = 'Подаци са главних метеоролошких станица'

STATIONS = {
    'pa': 'Палић',
    'so': 'Сомбор',
    'ns': 'Нови Сад',
    'bk': 'Б. Карловац',
    'lo': 'Лозница',
    'sm': 'С. Митровица',
    'va': 'Ваљево',
    'bg': 'Београд',
    'kg': 'Крагујевац',
    'sp': 'С. Паланка',
    'vg': 'В. Градиште',
    'cv': 'Црни Врх',
    'ne': 'Неготин',
    'zla': 'Златибор',
    'sj': 'Сјеница',
    'po': 'Пожега',
    'kv': 'Краљево',
    'kop': 'Копаоник',
    'ku': 'Куршумлија',
    'cu': 'Ћуприја',
    'ni': 'Ниш',
    'le': 'Лесковац',
    'za': 'Зајечар',
    'di': 'Димитровград'
}


def is_int(string):
    try:
        int(string)
        return True
    except ValueError:
        return False


def get_condition_code(language, condition):
    mapping = {
        'sr': {
            'Ведро':             'CodeSunny',
            'Делимично облачно': 'CodePartlyCloudy',
            'Магла':             'CodeFog',
            'Облачно':           'CodeCloudy',
            'Претежно ведро':    'CodeMostlySunny',
            'Претежно облачно':  'CodeMostlyCloudy'
        }
    }
    return mapping[language][condition]


def get_weather_report_page():
    url = 'http://www.hidmet.gov.rs/ciril/osmotreni/index.php'
    page = requests.get(url)
    return page


def parse_date(tree):
    text = tree.xpath("//h1//text()")[0]
    pattern = re.compile(r'^%s:  (.*)' % HEADER)
    match = pattern.search(text)
    date = match.group(1)
    return date


def parse_weather_report(tree, station):
    table = tree.xpath("//table/tr[td//text()[contains(., '%s')]]" % station)
    temperatura = table[0].xpath(".//td[2]//text()")[0].strip()
    pritisak = table[0].xpath(".//td[3]//text()")[0].strip()
    pravac_vetra = table[0].xpath(".//td[4]//text()")[0].strip()
    brzina_vetra = table[0].xpath(".//td[5]//text()")[0].strip()
    vlaznost = table[0].xpath(".//td[6]//text()")[0].strip()
    subj_osecaj_t = table[0].xpath(".//td[7]//text()")[0].strip()
    opis_vremena = table[0].xpath(".//td[9]//text()")[0].strip()

    return {
        'condition': get_condition_code('sr', opis_vremena),
        'data': [
            ('Станица', station, ''),
            ('Температура', int(temperatura), '°C'),
            ('Притисак', float(pritisak), 'hPa'),
            ('Правац ветра', pravac_vetra, ''),
            ('Брзина ветра', int(brzina_vetra), 'm/s') if is_int(brzina_vetra)
            else ('Брзина ветра', brzina_vetra, ''),
            ('Влажност ваздуха', int(vlaznost), '%'),
            ('Субјективни осећај', int(subj_osecaj_t), '°C'),
            ('Опис времена', opis_vremena, '')
        ]
    }


def parse_reports(dom_tree, stations):
    reports = []
    for station in stations:
        try:
            reports.append(parse_weather_report(dom_tree, station))
        except IndexError:
            print("Недостаје извештај из метеоролошке станице %s" % station,
                  file=sys.stderr)
        except Exception:
            print("Error parsing weather report from station: %s" % station,
                  sys.exc_info(), file=sys.stderr)
    return reports


def get_stations_by_abbrs(abbrs):
    return list(map(lambda x: STATIONS[x], abbrs))


def print_stations_list():
    for abbr in STATIONS:
        print(f"{abbr}\t%s" % STATIONS[abbr])


def filter_known_items(requested, known, not_found_msg):
    valid = []
    for item in requested:
        if item in known:
            valid.append(item)
        else:
            print(not_found_msg % item, file=sys.stderr)
    return valid


def parse_args(args):
    if args.list:
        print_stations_list()
        sys.exit(EXIT_SUCCESS)

    abbrs = filter_known_items(args.station, STATIONS, "Unknown weather station: %s")
    if len(abbrs) == 0:
        sys.exit(EXIT_NO_KNOWN_STATIONS)

    station_names = backend.hidmet.STATIONS.values() if args.all \
        else get_stations_by_abbrs(abbrs)
    return 'hidmet', station_names
