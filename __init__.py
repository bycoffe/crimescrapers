class BaseCrimeScraper(object):

    def save(self, data):
        """This is a placeholder method that should replaced with one that
        actually does something with the data, e.g. saves it to a data store.

        Each city's crime scraper class passes a dictionary of each crime's data 
        to save()
        """
        import pprint
        import datetime

        data['scraped_at'] = datetime.datetime.now()
        data['city'] = getattr(self, 'city', '')

        pprint.PrettyPrinter(4).pprint(data)


    def parse_date(self, date):
        """Try to parse a date string into a datetime object.

        This uses the python-dateutil library (http://labix.org/python-dateutil). 
        If the library cannot be imported, the original date
        will be returned.

        This method should be overridden if you'd like the
        date to be parsed differently.
        """
        if not isinstance(date, basestring):
            return date

        try:
            from dateutil import parser
        except ImportError:
            return date

        try:
            return parser.parse(date)
        except ValueError:
            return date


    def parse_address(self, *args, **kwargs):
        """To be overriden by each city subclass.
        """
        raise NotImplementedError


    def format_street(self, address):
        """Convert street address abbreviations to full words.
        """
        import re

        # The street abbreviations we want to convert.
        street_types = {'Ar': 'Arch',
                        'Arc': 'Arch',
                        'Av': 'Avenue',
                        'Ave': 'Avenue',
                        'Bd': 'Boulevard',
                        'Bl': 'Boulevard',
                        'Blvd': 'Boulevard',
                        'Cg': 'Crossing',
                        'Ch': 'Chase',
                        'Cir': 'Circle',
                        'Ci': 'Circle',
                        'Cl': 'Close',
                        'Cm': 'Commons',
                        'Co': 'Common',
                        'Cr': 'Circle',
                        'Cres': 'Crescent',
                        'Cs': 'Crescent',
                        'Ct': 'Court',
                        'Cv': 'Cove',
                        'Cw': 'Causeway',
                        'Cz': 'Cross',
                        'Dr': 'Drive',
                        'E': 'East',
                        'Ex': 'Extension',
                        'Ga': 'Gate',
                        'Gdns': 'Gardens',
                        'Geo': 'George',
                        'Hwy': 'Highway',
                        'Hy': 'Highway',
                        'Ld': 'Landing',
                        'La': 'Lane',
                        'Ln': 'Lane',
                        'Lo': 'Loop',
                        'Ky': 'Key',
                        'Ms': 'Muse',
                        'N': 'North',
                        'Pk': 'Parkway',
                        'Pkwy': 'Parkway',
                        'Pl': 'Place',
                        'Po': 'Post',
                        'Pt': 'Point',
                        'Pw': 'Parkway',
                        'Pz': 'Plaza',
                        'Qu': 'Quay',
                        'Rd': 'Road',
                        'Rh': 'Reach',
                        'Rn': 'Run',
                        'S': 'South',
                        'Sc': 'Shopping Center',
                        'Sh': 'Shoals',
                        'Sq': 'Square',
                        'St': 'Street',
                        'Tc': 'Trace',
                        'Te': 'Terrace',
                        'Ter': 'Terrace',
                        'Tl': 'Trail',
                        'Tk': 'Turnipke',
                        'Tr': 'Trail',
                        'Trl': 'Trail',
                        'Tp': 'Turnpike',
                        'W': 'West',
                        'Wa': 'Way',
                        'Wf': 'Warf',
                        'Wk': 'Walk',
                        'Wy': 'Way', }

        address = address.strip().title()

        # Create the regex for finding street abbreviations to convert.
        # This will look like \b(Ct|Rd|Bl|W)\b and be case-insensitive
        regex = re.compile(r'\b(%s)\b' % '|'.join(street_types.keys()), re.I)

        # Replace abbreviations with full words
        def repl(match):
            """Function to apply to regex matches for abbreviation
            replacement.
            """
            if match.group() in street_types.keys():
                return street_types[match.group()]

        address = regex.sub(repl, address)

        # Fix ordinal street numbers
        regex = re.compile(r'(\d(St|Nd|Rd|Th))')
        def ordrepl(match):
            """Function to apply to regex matches to fix ordinal case.
            (Changes 25Th Street to 25th Street, for example.)
            """
            return match.group().lower()

        address = regex.sub(ordrepl, address)

        # Fix street names such as McDonald to capitalize first D
        regex = re.compile(r'\b(Mcd)')
        def mcrepl(match):
            return 'McD'

        address = regex.sub(mcrepl, address)

        return address
