import re

from lxml.html import parse

from crimescraper import BaseCrimeScraper


class NewportNews(BaseCrimeScraper):

    city = 'Newport News'


    def run(self):
        for url in self.urls:
            doc = parse(url).getroot()
            rows = doc.cssselect('tr')

            for row in rows:
                data = self.parse_row(row)
                if not data: # Header row
                    continue
                self.save(data)


    def parse_row(self, row):

        fields = ['precinct',
                  'date',
                  'location',
                  'address',
                  'crime',
                  'status',
                  'disposition',
                  'beat',
                  'ra',
                  'employee',
                  'report_no', ]

        row = [cell.text for cell in row.cssselect('td')]

        if row[0] == 'PRECINCT': # Header row
            return None

        data = dict(zip(fields, row))
        data['date'] = self.parse_date(data['date'])
        data['block'], data['street1'], data['street2'] = self.parse_address(data['address'])
        data['crime'] = data['crime'].title()

        return data


    def parse_address(self, address):
        address = self.format_street(address)

        # There are 2 street names
        intersection = address.find('&') > 1 or address.find('/') > 1
        if intersection:
            street1, street2 = [x.strip() for x in re.split(r'\/|&', address)]
            return None, street1, street2

        # There is a block number and one street name
        block, street = [x.strip() for x in address.split('Blk')]
        return block, street, None


    @property
    def urls(self):
        """Create a list of daily URLs.
        """
        days = ['sun', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat', ]
        url = 'http://www2.nngov.com/newport-news/offenses/%stxt.htm'
        return [url % day for day in days]


if __name__ == '__main__':
    NewportNews().run()
