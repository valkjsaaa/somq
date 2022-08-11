from enum import IntEnum
from unittest import TestCase

from somq import MessageQueue


class Topic(IntEnum):
    A = 1
    B = 2
    C = 3

    @staticmethod
    def all() -> ['Topic']:
        return [e.value for e in Topic]


class TestMessageQueue(TestCase):
    def test_message_queue(self):
        mq = MessageQueue()
        q_all = mq.subscribe([Topic.A, Topic.B, Topic.C])
        q_a = mq.subscribe(Topic.A)
        q_b = mq.subscribe(Topic.B)
        # publish to all
        # noinspection PyTypeChecker
        mq.publish(Topic.all(), 'all')
        # test if a message is received by all
        self.assertEqual(q_all.get(block=False), 'all')
        # test if a message is received by a
        self.assertEqual(q_a.get(block=False), 'all')
        # test if a message is received by b
        self.assertEqual(q_b.get(block=False), 'all')
        # publish to a
        mq.publish(Topic.A, 'a')
        # test if a message is received by a
        self.assertEqual(q_a.get(block=False), 'a')
        # test if a message is received by b
        error = None
        try:
            q_b.get(block=False)
        except Exception as e:
            error = e
        self.assertIsNotNone(error)
        # test subscribe function
        test_message = None

        def f(message):
            nonlocal test_message
            test_message = message

        thread = mq.subscribe_function(Topic.A, f)
        # publish to a
        mq.publish(Topic.A, 'a')
        # test if a message is received by f
        self.assertEqual(test_message, 'a')
        thread.stop()
        mq.publish(Topic.A, 'b')
        self.assertEqual(test_message, 'a')
