from django.utils.functional import cached_property

from apps.core.helpers import Singleton
from apps.core.models import SiteConfiguration
from mq.common.exceptions import NonAuthorizedException


def check_non_authenticated(html: object, cookies: object, token: object) -> object:
    if 'Авторизація' in html:
        raise NonAuthorizedException(html, cookies, token)


class OpenDataBotKeyStorage(metaclass=Singleton):

    @cached_property
    def open_data_bot_key(self):
        return SiteConfiguration.get_solo().open_data_bot_key.key
