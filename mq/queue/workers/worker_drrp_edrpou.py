from apps.drrp.models import GroupDRRP, NumberDRRP, UnrecognizedItem
from apps.monitoring.manager.manager import MonitoringManagerFacade
from mq.mq_queue.loaders.drrp_edrpou import DrrpEdrpouLoader
from mq.mq_queue.workers import AbstractWorker


class DRRPEdrpouWorker(AbstractWorker):
    loader = DrrpEdrpouLoader()
    manager = MonitoringManagerFacade()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.group = GroupDRRP.objects.filter(id=self.message_content).first()

    async def process(self):
        if not self.group:
            self.logger.info("Can not find GroupDRRP with ID={}".format(self.message_content))
            return

        number, offset = 20_000, 0
        await self.load_and_process(number, offset)

    async def load_and_process(self, number, offset):
        self.logger.info('Start loading: {} offset: {}'.format(number, offset))
        response = await self.loader.load(self.group.edrpou, self.group.edrpou_role, number, offset, self.logger)
        self.process_response(response)

        if response['data']['count'] > number + offset:
            self.logger.info('Count > than loaded: {}. Has one more page'.format(response['data']['count']))
            offset += number
            await self.load_and_process(number, offset)

    def process_response(self, response):
        self.logger.info('Start processing response: {} items'.format(len(response['data']['items'])))
        numbers = []
        for item in response['data']['items']:
            if str(item['dcGroupType']) == "1":
                self.create_unrecognized(item)
                continue

            numbers.append(NumberDRRP(group_id=self.group.id, number=item['name']))

        self.logger.info('Saving to db...')
        numbers = NumberDRRP.objects.bulk_create(numbers)
        self.push_to_queue(numbers)
        self.logger.info('Saved.')

    def push_to_queue(self, numbers):
        self.logger.info('Pushing numbers to queue.')
        self.manager.load_drrp_coordinates_numbers(numbers)

    def create_unrecognized(self, item):
        UnrecognizedItem.objects.create(
            group_id=self.group.id,
            name=item['name'],
        )
