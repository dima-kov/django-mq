from django.conf import settings

from apps.monitoring.models import LandPlotInfo, ParsingItem, RestrictionExtended
from apps.monitoring.models import RestrictionShort
from apps.monitoring.models import LandOwner
from apps.monitoring.models import SubstantiveLawSubject
from mq.mq_queue.common.db_normalizers import DateNormalizer, NotFoundNormalizer


FIELDS_NORMALIZE = {
    'register_date': DateNormalizer(),
    'restriction_register_date': DateNormalizer(),
}

NOT_FOUND_NORMALIZER = NotFoundNormalizer()

LAND_INFO_ATTRS = {
    "Цільове призначення": 'aim',
    "Форма власності": 'ownership',
    "Площа земельної ділянки": 'square',
    "Місце розташування": 'location',
}

LAND_OWNER_ATTRS = {
    "Прізвище, ім'я та по батькові фізичної особи": 'name',
    'Найменування юридичної особи': 'legal_entity_name',
    'Код ЄДРПОУ юридичної особи': 'edrpou',
    "Дата державної реєстрації права (в державному реєстрі прав)": 'register_date',
    "Номер запису про право (в державному реєстрі прав)": 'record_number',
    "Орган, що здійснив державну реєстрацію права (в державному реєстрі прав)": 'registration_agency',
}

SUBSTANTIVE_LAW_SUBJECT_ATTRS = {
    'Вид речового права': 'property_law_type',
    "Прізвище, ім'я та по батькові фізичної особи": 'name',
    'Найменування юридичної особи': 'legal_entity_name',
    'Код ЄДРПОУ юридичної особи': 'edrpou',
    'Дата державної реєстрації права (в державному реєстрі прав)': 'register_date',
    'Номер запису про право (в державному реєстрі прав)': 'record_number',
    'Орган, що здійснив державну реєстрацію права (в державному реєстрі прав)': 'registration_agency',
    "Площа, на яку поширюється право суборенди": 'square',
}

RESTRICTION_SHORT_ATTRS = {
    'Вид обмеження': 'restriction_type',
    'Дата державної реєстрація обмеження': 'register_date',
}

RESTRICTION_EXTENDED_ATTRS = {
    'Вид обмеження': 'restriction_type',
    'Дата державної реєстрація обмеження': 'restriction_register_date',
    'Вид речового права': 'substantive_law_type',
    'Найменування юридичної особи': 'legal_entity_name',
    "Прізвище, ім'я та по батькові фізичної особи": 'name',
    'Код ЄДРПОУ юридичної особи': 'edrpou',
    'Дата державної реєстрації речового права': 'register_date',
    'Номер запису про речове право': 'record_number',
    'Орган, що здійснив державну реєстрацію речового права': 'registration_agency',
}

TYPES__ATTRS_MAP = {
    settings.LAND_INFO: LAND_INFO_ATTRS,
    settings.LAND_OWNER: LAND_OWNER_ATTRS,
    settings.SUBSTANTIVE_LAW_SUBJECT: SUBSTANTIVE_LAW_SUBJECT_ATTRS,
    settings.RESTRICTION_SHORT: RESTRICTION_SHORT_ATTRS,
    settings.RESTRICTION_EXTENDED: RESTRICTION_EXTENDED_ATTRS,
}

TYPES__MODELS_MAP = {
    settings.LAND_INFO: LandPlotInfo,
    settings.LAND_OWNER: LandOwner,
    settings.SUBSTANTIVE_LAW_SUBJECT: SubstantiveLawSubject,
    settings.RESTRICTION_SHORT: RestrictionShort,
    settings.RESTRICTION_EXTENDED: RestrictionExtended,
}


class SaverDB(object):

    def __init__(self, parsing_item: ParsingItem):
        self.parsing_item = parsing_item

    def create(self, block_type, data):
        obj = TYPES__MODELS_MAP[block_type]()
        obj = self._set_attrs(obj, data, TYPES__ATTRS_MAP[block_type])
        obj.parsing_item = self.parsing_item
        obj.save()

    def save_html(self, html):
        self.parsing_item.html = html
        self.parsing_item.save()

    def not_found(self):
        self.parsing_item.make_not_found()

    def _set_attrs(self, obj, data, fields):
        for table_key, table_value in data.items():
            attr_name = self._get_model_field_name_by_html_label(table_key.strip(), fields)
            value = self._normalize_value(attr_name, table_value)
            setattr(obj, attr_name, value)
        return obj

    @staticmethod
    def _normalize_value(attr_name, value):
        value = NOT_FOUND_NORMALIZER.normalize(value)

        normalizer = FIELDS_NORMALIZE.get(attr_name, None)
        if normalizer is not None and value is not None:
            value = normalizer.normalize(value)
        return value

    @staticmethod
    def _get_model_field_name_by_html_label(html_label, labels_fields_map):
        """
        :param html_label: label for which we are looking a field name
        :param labels_fields_map: dict where saved labels and corresponding them field names
            labels_fields_map = {
                'Цільове призначення': 'aim',
                ...
            }
        :return: field name. (E.g. 'aim')
        """
        for label, field_name in labels_fields_map.items():
            if label in html_label or label == html_label:
                return field_name
