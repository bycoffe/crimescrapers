import datetime

from lxml.html import parse, submit_form

from crimescraper import BaseCrimeScraper


class Portsmouth(BaseCrimeScraper):

    city = 'Portsmouth'


    def run(self, days_back=7):
        url = 'http://www.portsmouthva.gov/ppd/ArrestIncidents/incidentsearch.aspx'
        doc = parse(url).getroot()

        doc = parse(submit_form(doc.forms[0])).getroot()
        rows = doc.cssselect('tr')

        min_date = datetime.date.today() - datetime.timedelta(days_back)

        for row in rows[1:]:
            data = self.parse_row(row, min_date)

            # parse_row will return false if it's before min_date
            if not data: 
                break

            self.save(data)


    def parse_row(self, row, min_date):

        fields = ['report_number', 
                  'date', 
                  'time', 
                  'crime', 
                  'att-com',
                  'block', 
                  'street', 
                  'tract', ]

        row = [cell.text for cell in row.cssselect('font')]

        data = dict(zip(fields, row))

        data['datetime'] = self.parse_date('%(date)s %(time)s' % data)
        if data['datetime'].date() < min_date:
            return None

        data['street'] = self.format_street(data['street'])
        data['crime'] = data['crime'].title()

        return data


if __name__ == '__main__':
    Portsmouth().run(days_back=5)
