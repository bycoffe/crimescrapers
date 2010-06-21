import datetime
import urllib
import urllib2

from lxml.html import fromstring

from crimescraper import BaseCrimeScraper


class Norfolk(BaseCrimeScraper):

    city = 'Norfolk'
    headers = {'User-Agent': 'Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 6.0)'}


    def run(self):
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
        urllib2.install_opener(self.opener)

        disclaimer_page = self.accept_disclaimer()
        map_page = self.get_map_page()
        print_page = self.get_print_page()

        for data in self.parse_print_page(print_page):
            self.save(data)


    def accept_disclaimer(self):
        url = 'http://gis.norfolk.gov/crimeviewcommunity/default.asp'
        query = urllib.urlencode({'fldAccept': 'yes'})

        request = urllib2.Request(url, query, self.headers)
        return urllib2.urlopen(request).read()


    def get_print_page(self):
        values = {'splash': 'f',
                  'print': 'true',
                  'sortfield': 'CVCLEGEND',
                  'sortorder': 'ASC',
                  'detail': 'true',
                  'windowwidth': '1015',
                  'windowheight': '697', }
        query = urllib.urlencode(values)
        url = 'http://gis.norfolk.gov/crimeviewcommunity/report.asp?%s' % query

        request = urllib2.Request(url, query, self.headers)
        return urllib2.urlopen(request).read()


    def parse_print_page(self, page):

        fields = ['case_number',
                  'crime',
                  'description',
                  'date',
                  'time',
                  'location', ]

        doc = fromstring(page)
        rows = doc.cssselect('tr')
        for row in rows[1:]:
            data = [cell.text for cell in row.cssselect('td')]
            if data[0] == '#':
                continue
            data = dict(zip(fields, data[1:]))

            data['datetime'] = self.parse_date('%(date)s %(time)s' % data)
            data['block'], data['street'] = self.parse_address(data['location'])
            data['crime'] = data['crime'].title()

            yield data


    def parse_address(self, location):
        try:
            block, street = location.split(' BLOCK ')
        except ValueError: # There is no 'BLOCK' in the string
            block, street = 0, location

        block = (None if block == 'UNIT' else block)
        street = self.format_street(street)

        return block, street


    def get_map_page(self):
        self.headers['Referer'] = 'http://gis.norfolk.gov/crimeviewcommunity/wizard.asp'
        request = urllib2.Request(self.map_url, None, self.headers)
        return urllib2.urlopen(request).read()


    @property
    def map_url(self):
        end_date = datetime.date.today().strftime('%Y%m%d')
        start_date = (datetime.date.today() -
                datetime.timedelta(7)).strftime('%Y%m%d')

        values = {'mapfunction1': '51',
                  'mapFunction2': '40',
                  'queryName2': 'CityLimit_Select',
                  'queryValue2': 'Norfolk',
                  'maplayeractivebyid2': 'CITY_LIMIT',
                  'maplayervisiblebyid2': 'CITY_LIMIT',
                  'bufferDistance3': '0',
                  'bufferUnits3': '0',
                  'bufferSource3': '2',
                  'bufferTarget3': '0',
                  'mapFunction3': '25',
                  'mapFunction4': '34',
                  'mapFunction5': '76',
                  'mapFunction6': '37',
                  'maplayeractivebyid7': 'CVC_INCIDENT',
                  'maplayervisiblebyid7': 'CVC_INCIDENT',
                  'windowwidth': '938',
                  'windowheight': '531', }

        query = urllib.urlencode(values)

        # We don't want to encode this part.
        query += "&whereExpr4=((CVDATE%3E=" + start_date + ")%20AND%20(CVDATE%3C=" + end_date + "))%20AND%20(CVCQUERY%20IN%20('AGGRAVATED%20ASSAULT','ARSON','BURGLARY','HOMICIDE','LARCENY%20-%20FROM%20AUTO/OF%20AUTO%20PARTS','LARCENY%20(OTHER)','NARCOTICS%20VIOLATIONS','PROSTITUTION','RAPE','ROBBERY','SIMPLE%20ASSAULT','STOLEN%20VEHICLE','VANDALISM'))"

        url = 'http://gis.norfolk.gov/crimeviewcommunity/map.asp?%s' % query
        return url


if __name__ == '__main__':
    Norfolk().run()
