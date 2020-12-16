from mq.facade import QueuesFacade


def get_queues_stats():
    queues = QueuesFacade.all
    return {q.name: get_queue_stats(q) for q in queues}


def get_queue_stats(queue):
    return {
        'wait': queue.len_wait(),
        'processing': queue.len_processing(),
        'consumers': queue.consumers.as_bits(),
    }
