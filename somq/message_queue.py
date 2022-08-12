import itertools
import queue
import threading
from typing import Generic, TypeVar, Callable, Union, List, Tuple, Set

Object = TypeVar('Object')


class ListeningThread(threading.Thread):
    # noinspection PyShadowingNames
    def __init__(self, message_queue: 'MessageQueue', queue: queue.Queue, function: Callable[[Object], None]):
        super().__init__()
        self.message_queue = message_queue
        self.queue = queue
        self.function = function
        self.running = True
        self.start()

    def run(self):
        while self.running:
            message = self.queue.get()
            if self.running:
                self.function(message)
                self.queue.task_done()

    def stop(self):
        self.running = False
        self.queue.put(None)
        self.join()
        self.message_queue.unsubscribe(self.queue)


class MessageQueue(Generic[Object]):

    def __init__(self):
        self.queues: [Tuple[Set[str], queue.Queue[Object]]] = []

    def subscribe(self, topics: Union[List[str], str]) -> queue.Queue[Object]:
        """
        Subscribe to a topic.
        :param topics: The list of topics or topic to subscribe to.
        :return: The queue to receive messages on.
        """
        q = queue.Queue()
        if not isinstance(topics, list):
            topics = [topics]
        topics = set(topics)
        self.queues.append((topics, q))
        return q

    def publish(self, topic: Union[List[str], str], message: Object):
        """
        Publish a message to a list of topics or a topic.
        :param topic: The list of topics or topic to publish to.
        :param message: The message to publish.
        """
        if not isinstance(topic, list):
            topic = [topic]
        topic = set(topic)
        for t, q in self.queues:
            for t1, t2 in itertools.product(topic, t):
                if t1.startswith(t2):
                    q.put(message)
                    break

    def unsubscribe(self, q: queue.Queue[Object]):
        """
        Unsubscribe from a topic.
        :param q: The queue to unsubscribe from.
        :return:
        """
        for t, q2 in self.queues:
            if q2 == q:
                self.queues.remove((t, q))
                return
        raise ValueError('Queue not found')

    def subscribe_function(self, topics: Union[List[str], str], f: Callable[[Object], None]) -> ListeningThread:
        """
        Subscribe to a topic and call a function when a message is received.
        :param topics: The list of topics or topic to subscribe to.
        :param f: The function to call when a message is received.
        :return: The listening thread.
        """
        q = self.subscribe(topics)
        thread = ListeningThread(self, q, f)
        return thread
