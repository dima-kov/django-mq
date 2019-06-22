from mq.loaders.abstract import AuthenticatedLoader


class PdfLoader(AuthenticatedLoader):

    async def load(self, entity, logger):
        pdf_link = entity

        return await self.async_requester.GET_request_binary(
            pdf_link, self.cookies, verify_ssl=False,
        )
