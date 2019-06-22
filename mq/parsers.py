import re
import logging

from bs4 import BeautifulSoup, NavigableString
from django.conf import settings

from apps.monitoring.models import ParsingItem
from mq.common.db_saver import SaverDB
from mq.common.exceptions import NoTableInsideHtml

IGNORE_FIELDS = ['Кадастровий номер земельної ділянки']


class BaseParser(object):
    main_logger = logging.getLogger(settings.MONITORING_MAIN_LOGGER_NAME)


class TokenParser(BaseParser):

    def parse_token(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        input = soup.find("input", {"name": "cadastre_find_by_cadnum[_token]"})
        if input is None:
            self.main_logger.info("Input is none. html:")
            self.main_logger.debug(html)
            return None
        result = input['value']
        return result


class TransactionTokenParser(BaseParser):

    def parse(self, html):
        regex = r"id=\"cadastre_find_by_cadnum_token\" name=\"cadastre_find_by_cadnum\[token\]\" value=\"\w{40}\" \/><div "
        token = re.search(regex, html)
        if token:
            return self.regex_only_token(token.group())
        return

    @staticmethod
    def regex_only_token(token_html):
        token = re.search(r"\w{40}", token_html)
        if token:
            return token.group()
        return None


class NumberParser(BaseParser):

    def __init__(self, parsing_item: ParsingItem, html, logger=None):
        self.parsing_item = parsing_item
        self.html = html
        self.logger = logger or logging.getLogger("html-parser")
        self.db_saver = SaverDB(parsing_item)
        self.db_saver.save_html(html)
        self.soup = BeautifulSoup(self.html, 'html.parser')

    def parse(self):
        self.logger.info('Start parsing')
        not_found = self.check_not_found(self.html)
        if not_found:
            self.logger.info('Not found')
            self.db_saver.not_found()
            return

        self.parse_table()

    def parse_table(self):
        table = self.get_table_html()

        block_type = ''
        properties = []
        for tr in table.find_all('tr'):
            if isinstance(tr, NavigableString):
                continue

            tds = tr.find_all('td')
            if len(tds) == 1:
                if self.td_is_header(tds[0]):
                    self.process_previous_block(block_type, properties)
                    block_type = self.get_header_type(tds[0])
                    properties = [{}]
                elif self.td_is_restriction_extended_divider(tds[0]):
                    continue
                else:
                    properties.append({})
            else:
                label = tds[0].text.strip()
                if label in IGNORE_FIELDS:
                    continue

                properties[-1][label] = tds[1].text.strip()

        self.process_previous_block(block_type, properties)
        self.logger.info('Parsed and created in db!')

    def get_table_html(self):
        tables = self.soup.find_all("table", {"class": "table table-bordered"})
        if len(tables) == 0:
            raise NoTableInsideHtml(self.html)
        return tables[0]

    def parse_pdf_link(self):
        if not self.parsing_item.not_found:
            footer_div = self.soup.find_all("div", {"class": "box-footer"})[0]
            return footer_div.find('a')['href']

    def process_previous_block(self, block_type, properties):
        if properties is None:
            return

        block_type = self.check_restrictions_block(block_type, properties)

        for data in properties:
            self.db_saver.create(block_type, data)

    def get_header_type(self, td):
        if self.td_is_land_info(td):
            return settings.LAND_INFO

        elif self.td_is_property_owner(td):
            return settings.LAND_OWNER

        elif self.td_is_legal_owner(td):
            return settings.SUBSTANTIVE_LAW_SUBJECT

        elif self.td_is_restriction_short(td):
            return settings.RESTRICTION_SHORT

        elif self.td_is_restriction_extended(td):
            return settings.RESTRICTION_EXTENDED

        return settings.DIVIDER

    @staticmethod
    def td_is_land_info(td):
        return 'Відомості про земельну ділянку' in td.text

    @staticmethod
    def td_is_property_owner(td):
        return "Відомості про суб'єктів права власності на земельну ділянку" in td.text

    @staticmethod
    def td_is_legal_owner(td):
        return "Відомості про суб'єкта речового прав" in td.text

    @staticmethod
    def td_is_restriction_short(td):
        return 'Відомості про зареєстроване обмеження у використанні земельної ділянки' in td.text

    @staticmethod
    def td_is_restriction_extended(td):
        return "Відомості про зареєстроване обмеження у використанні земельної ділянки" in td.text

    @staticmethod
    def td_is_restriction_extended_divider(td):
        return "Відомості про суб'єкта речового права" in td.text

    @staticmethod
    def td_is_header(td):
        class_list = td.get('class', None)
        if class_list is None or len(class_list) == 0:
            return False
        if class_list[0] == 'td-header':
            return True
        return False

    @staticmethod
    def check_not_found(html):
        full_regex = r"Інформація про земельну ділянку з вказаним Вами кадастровим номером " \
                     "\((\d{10}:\d{2}:\d{3}:\d{4})\) не знайдена в Державному земельному кадастрі"
        only_cadastral_regex = r"(\d{10}:\d{2}:\d{3}:\d{4})"

        matches = re.search(full_regex, html, re.MULTILINE)

        if matches:
            error_message = matches.group()
            matches_cadastral = re.search(only_cadastral_regex, error_message)
            return matches_cadastral.group(), error_message
        return None

    @staticmethod
    def check_restrictions_block(block_type, properties):
        if block_type in [settings.RESTRICTION_SHORT, settings.RESTRICTION_EXTENDED]:
            if len(properties[0]) <= 2:
                return settings.RESTRICTION_SHORT
            return settings.RESTRICTION_EXTENDED
        return block_type


class MonetaryValueParser(object):

    def __init__(self, parsing_item: ParsingItem, html, logger=None):
        self.parsing_item = parsing_item
        self.html = html
        self.logger = logger or logging.getLogger("html-parser")
        self.db_saver = SaverDB(parsing_item)
        self.db_saver.save_html(html)
        self.soup = BeautifulSoup(self.html, 'html.parser')
