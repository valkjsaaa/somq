Simple Object-based Message Queue
=================================
Jackie Yang
-----------

Installation:
```
pip install somq
```

Usage:

```python
import time
from enum import IntEnum
from somq import MessageQueue


class Topic(IntEnum):
    A = 1
    B = 2
    C = 3

    @staticmethod
    def all() -> ['Topic']:
        return [e.value for e in Topic]


mq = MessageQueue()
q_all = mq.subscribe([Topic.A, Topic.B, Topic.C])
q_a = mq.subscribe(Topic.A)
# publish to all
mq.publish(Topic.all(), 'all')
# publish to a
mq.publish(Topic.A, 'a')
# receive from all
print(q_all.get())
print(q_all.get())
# print 'all' and 'a'
# receive from a
print(q_a.get())
# print 'a'
# use a function to subscribe to a topic
thread = mq.subscribe_function(Topic.A, lambda x: print(x))
# publish to a
mq.publish(Topic.A, 'a')
# print 'a'
time.sleep(0.1)
# stop the thread
thread.stop()
```

