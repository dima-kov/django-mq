from datetime import datetime


class Normalizer(object):

    def normalize(self, value):
        raise NotImplemented


class NotFoundNormalizer(Normalizer):

    def normalize(self, value):
        if value == 'Інформація відсутня':
            value = None
        return value


class DateNormalizer(Normalizer):

    def normalize(self, value):
        return datetime.strptime(value, '%d.%m.%Y')
