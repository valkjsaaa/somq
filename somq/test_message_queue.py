import time
from enum import IntEnum
from unittest import TestCase

from somq import MessageQueue


class TestMessageQueue(TestCase):
    def test_message_queue(self):
        mq = MessageQueue()
        q_all = mq.subscribe('')
        q_ab = mq.subscribe(['a', 'b'])
        q_a = mq.subscribe('a')
        q_b = mq.subscribe('b')
        # publish to all
        # noinspection PyTypeChecker
        mq.publish('a_test', 'a')
        # test if a message is received by all
        self.assertEqual(q_all.get(block=False), 'a')
        error = None
        try:
            q_all.get(block=False)
        except Exception as e:
            error = e
        self.assertIsNotNone(error)
        # test if a message is received by a
        self.assertEqual(q_a.get(block=False), 'a')
        error = None
        try:
            q_a.get(block=False)
        except Exception as e:
            error = e
        self.assertIsNotNone(error)
        # test if a message is received by b
        error = None
        try:
            q_b.get(block=False)
        except Exception as e:
            error = e
        self.assertIsNotNone(error)
        # test if a message is received by ab
        self.assertEqual(q_ab.get(block=False), 'a')
        error = None
        try:
            q_ab.get(block=False)
        except Exception as e:
            error = e
        self.assertIsNotNone(error)
        # test subscribe function
        test_message = None

        def f(message):
            nonlocal test_message
            test_message = message

        thread = mq.subscribe_function('a', f)
        # publish to a
        mq.publish('a', 'a')
        # test if a message is received by f
        time.sleep(0.1)
        self.assertEqual(test_message, 'a')
        thread.stop()
        mq.publish('b', 'b')
        self.assertEqual(test_message, 'a')
