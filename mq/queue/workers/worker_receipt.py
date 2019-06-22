from django.db import transaction

from apps.monitoring.models import ParsingItem
from mq.mq_queue.loaders import ReceiptLoader
from mq.mq_queue.workers import AbstractWorker
from apps.receipts.models import Receipt, Debtor


class ReceiptWorker(AbstractWorker):
    receipt_loader = ReceiptLoader()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parsing_item: ParsingItem = ParsingItem.objects.filter(id=self.message_content).first()

    async def process(self):
        if not self.parsing_item:
            self.logger.info("Can not find ParsingItem with ID={}".format(self.message_content))
            return

        self.logger.info("Receipt worker start: {}".format(self.parsing_item.id))
        response = await self.receipt_loader.load(self.parsing_item.number.number, self.logger)
        return self.process_response(response)

    def process_response(self, response):
        self.logger.info('Receipt response: {}'.format(response))
        items = response['items']

        for item in items:
            with transaction.atomic():
                self.create_receipt(item)

    def create_receipt(self, item):
        receipt = Receipt.objects.create(
            type=int(item.get('type', None)),
            crr_id=item.get('id'),
            cr_number=item.get('crNumber'),
            cr_date=item.get('crDate'),
            deadline=item.get('deadline'),
            parsing_item=self.parsing_item,
        )
        self.create_debtors(receipt, item.get('debtors', []))

    def create_debtors(self, receipt, debtors):
        Debtor.objects.bulk_create(
            [Debtor(receipt_id=receipt.id, crr_id=d.get('id'), name=d.get('fullName'))
             for d in debtors]
        )
