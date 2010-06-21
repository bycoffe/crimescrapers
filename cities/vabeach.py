import time
import urllib2

from lxml.html import fromstring

from crimescraper import BaseCrimeScraper


class VirginiaBeach(BaseCrimeScraper):

    city = 'Virginia Beach'


    def run(self, start_id=1):
        page_id = start_id
        url = 'https://wwws.vbgov.com/ePRO/MainUI/Incidents/IncidentReport.aspx?id=%s'

        # We need to be able to accept cookies for requests to the 
        # incident report pages to be successful.
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
        urllib2.install_opener(opener)

        while True:
            # Continue finding reports, adding 1 to the page_id
            # with each loop, until, a page with the current
            # page_id cannot be retrieved.
            try:
                response = urllib2.urlopen(url % page_id)
            except urllib2.HTTPError:
                break

            doc = fromstring(response.read())
            data = self.parse_page(doc)
            data['page_id'] = page_id
            self.save(data)

            page_id += 1
            time.sleep(1)


    def parse_page(self, doc):

        fields = {'location': 'lblLocation',
                  'reported': 'lblDateReported',
                  'occurred': 'lblDateOccur',
                  'subdivision': 'lblSubDivName',
                  'crime': 'dLstCrimes__ctl0_lblCrime', }

        data = {}
        for key, value in fields.iteritems():
            data[key] = doc.get_element_by_id(value).text

        data['case_number'] = doc.get_element_by_id('lblCaseNo') \
                .cssselect('font')[0].text \
                .replace('Case#: ', '')

        data['reported'] = self.parse_date(data['reported'])
        data['occurred'] = self.parse_date(data['occurred'])

        data['block'], data['street'] = self.parse_address(data['location'])
        data['neighborhood'] = data['subdivision'].title()

        return data


    def parse_address(self, location):
        block, street = location.split('-BLK    ')
        street = self.format_street(street)
        return block, street


if __name__ == '__main__':
    VirginiaBeach().run(start_id=1)
