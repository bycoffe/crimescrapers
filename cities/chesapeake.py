import csv
import re
import urllib2

from crimescraper import BaseCrimeScraper


class Chesapeake(BaseCrimeScraper):

    city = 'Chesapeake'


    def run(self):
        url = 'http://www.chesapeake.va.us/services/depart/police/police/downloads/dcr/dcr-text.csv'

        response = urllib2.urlopen(url)
        reader = csv.DictReader(response)

        for data in reader:
            data['from'] = self.parse_date('%(FDate)s %(FTime)s' % data)
            data['to'] = self.parse_date('%(TDate)s %(TTime)s' % data)

            (data['street1'], 
                 data['street2'], 
                 data['unit'], 
                 data['block']) = self.parse_address(data['Block#'], 
                                                    data['Street name'])
             
            self.save(data)


    def parse_address(self, block, street):
        street1 = self.format_street(street)
        street1, unit = self.get_unit(street1)
        street2 = None

        block = block or None

        # Check whether this is an intersection
        if re.search(r'\/', street1):
            street1, street2 = [self.format_street(x)
                                                for x in 
                                                street1.split('/')]

        return street1, street2, unit, block


    def get_unit(self, street):
        """Separate the unit and the street in a street name.
        """
        regex = re.compile(r'(#|Unit)')
        if not regex.search(street):
            return street, None

        street, unit_type, unit = [x.strip() for x in regex.split(street)]
        unit = ' '.join([unit_type, unit])

        return street, unit


if __name__ == '__main__':
    Chesapeake().run()

