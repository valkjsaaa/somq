import queue
import threading
from enum import Enum
from typing import Generic, TypeVar, Callable, Union, List

Topic = TypeVar('Topic', bound=Enum)
Object = TypeVar('Object')


class ListeningThread(threading.Thread):
    # noinspection PyShadowingNames
    def __init__(self, topic: Topic, queue: queue.Queue, function: Callable[[Object], None]):
        super().__init__()
        self.topic = topic
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


class MessageQueue(Generic[Topic, Object]):

    def __init__(self):
        self.queues: {Topic: [queue.Queue[Object]]} = {}

    def subscribe(self, topics: Union[List[Topic], Topic]) -> queue.Queue[Object]:
        """
        Subscribe to a topic.
        :param topics: The list of topics or topic to subscribe to.
        :return: The queue to receive messages on.
        """
        q = queue.Queue()
        if isinstance(topics, list):
            for topic in topics:
                if topic not in self.queues:
                    self.queues[topic] = []
                self.queues[topic].append(q)
        else:
            if topics not in self.queues:
                self.queues[topics] = []
            self.queues[topics].append(q)
        return q

    def publish(self, topic: Union[List[Topic], Topic], message: Object):
        """
        Publish a message to a list of topics or a topic.
        :param topic: The list of topics or topic to publish to.
        :param message: The message to publish.
        """
        if isinstance(topic, list):
            for t in topic:
                if t in self.queues:
                    for q in self.queues[t]:
                        q.put(message)
        else:
            if topic in self.queues:
                for q in self.queues[topic]:
                    q.put(message)

    def unsubscribe(self, q: queue.Queue[Object]):
        """
        Unsubscribe from a topic.
        :param q: The queue to unsubscribe from.
        :return:
        """
        for topic in self.queues:
            if q in self.queues[topic]:
                self.queues[topic].remove(q)
                if not self.queues[topic]:
                    del self.queues[topic]
                break

    def subscribe_function(self, topics: Union[List[Topic], Topic], f: Callable[[Object], None]) -> ListeningThread:
        """
        Subscribe to a topic and call a function when a message is received.
        :param topics: The list of topics or topic to subscribe to.
        :param f: The function to call when a message is received.
        :return: The listening thread.
        """
        q = self.subscribe(topics)
        thread = ListeningThread(topics, q, f)
        return thread
