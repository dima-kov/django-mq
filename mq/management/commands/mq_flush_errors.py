from django.conf import settings
from django.core.management import BaseCommand, CommandError
from django.utils import timezone

from mq.models import MqError


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '-d', '--dry', action='store_true',
            help='Dry run: just output number of errors to delete,'
                 'but do not performs delete query',
        )
        parser.add_argument(
            '-vvv', '--verbose', action='store_true',
            help='Verbose mode, Output filter query',
        )

    def handle(self, *args, **options):
        dry = options['dry']
        verbose = options['verbose']

        if settings.MQ_FLUSH_ERRORS_DAYS is None:
            raise CommandError(
                'settings.MQ_FLUSH_ERRORS_DAYS is None. Please set number '
                'of days after which resolved errors will be deleted'
            )
        shift = timezone.now() - timezone.timedelta(days=settings.MQ_FLUSH_ERRORS_DAYS)
        errors = MqError.objects.filter(status=MqError.REVIEWED, raised_at__lte=shift)
        self.stdout.write("To delete: {}".format(errors.count()))

        if verbose:
            self.stdout.write("Query:\n{}".format(errors.query))

        if not dry:
            deleted = errors.delete()
            self.stdout.write("Deleted: {}".format(deleted))
