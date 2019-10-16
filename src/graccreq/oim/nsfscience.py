"""
Add NSF Field of Science to GRACC records

"""
import csv
import urllib2



class NSFScience(object):
    """
    Add the OIM_NSFFieldOfScience attribute to jobs
    """

    def __init__(self, url="file:///etc/nsffieldofscience.csv"):
        """

        """
        self.mapping_csv = url
        self._parseFields(self.mapping_csv)


    def _parseFields(self, url):
        raw_csv = urllib2.urlopen(url)
        parsed_csv = csv.reader(raw_csv, delimiter=',')

        self.mapping_dict = {}
        for row in parsed_csv:
            self.mapping_dict[row[0]] = row[1]


    def parseDoc(self, record):
        """
        Parse the current record.  Look for the attribute OIM_FieldOfScience and map
        to the OIM_NSFFieldOfScience

        :returns: Minimal dict with attributes to add
        """
        if 'OIM_FieldOfScience' in record:
            if record['OIM_FieldOfScience'] in self.mapping_dict:
                return {'OIM_NSFFieldOfScience': self.mapping_dict[record['OIM_FieldOfScience']]}

        return {}



if __name__ == "__main__":
    science = NSFScience(url="file:///Users/derekweitzel/git/gracc-reporter/tests/mapping-table-test.csv")
    example_dict = {'OIM_FieldOfScience': 'Computational Condensed Matter Physics'}
    print science.parseDoc(example_dict)
