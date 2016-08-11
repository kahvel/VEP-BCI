from parsers import FeaturesParser


class ColumnsIterator(object):
    def __init__(self):
        pass

    def iterateColumns(self, columns, extraction_method_names):
        for key in sorted(columns):
            method = FeaturesParser.getMethodFromFeature(key)
            if method in extraction_method_names:
                yield method, columns[key]
