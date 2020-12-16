# django-mq

## Installation

Install is possible either with SSH access to github account with read permission to repository:
  `pip install git+ssh://git@github.com/feodal-online/django-mq.git@master`

or with Github access token:
  `pip_install_privates --token {GITHUB_TOKEN} git+ssh://git@github.com/feodal-online/django-mq.git@master`

## Setup:

1. Add `mq` to INSTALLED_APPS, make sure to place above `django.contrib.admin` to include functionality of queues in admin
1. Set redis settings:
    ```
    MQ_REDIS_HOST = 'localhost'
    MQ_REDIS_PORT = 6379
    ```
1. Set logging:
    ```
    MQ_LOGGING_DIRECTORY = '/tmp/project-mq-log/'
    MQ_LOGGING_LOGGERS = [
       'logger_foo',
       'logger_bar',
    ]
    from mq.logging import configure_logging
    
    configure_logging(LOGGING, MQ_LOGGING_LOGGERS, MQ_LOGGING_DIRECTORY)
    ```
1. Set a class with queues facade. It is used for admin stats view: (/admin/mq/mqmessagetype/stats/).
   
    This class should be inherited from `mq.queue.queue.BaseQueuesFacade`:
    ```
    MQ_QUEUES_FACADE_CLASS = 'myapp.facade.QueuesFacade`
    ```
  
## Settings

- `MQ_FLUSH_ERRORS_DAYS` - specify days after which resolved `MqError`s will be deleted with command `mq_flush_errors`  

### Django vs non django usage
App supports to be used with and without django.
