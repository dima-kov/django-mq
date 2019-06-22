from apps.drrp.models import NumberDRRP
from mq.workers import CoordinatesWorker


class DRRPCoordinatesWorker(CoordinatesWorker):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.number = NumberDRRP.objects.filter(id=self.message_content).first()

    def process_response(self, response):
        X, Y = super().process_response(response)
        if X is None or Y is None:
            X, Y = 0.0, 0.0

        return X, Y
