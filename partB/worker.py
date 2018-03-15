import os
import socket
import sys
from math import sqrt
import Pyro4
from Pyro4.util import SerializerBase
from work_item import WorkItem

# For 'work_item.WorkItem' we register a deserialisation hook to be able to get these back from Pyro
SerializerBase.register_dict_to_class("work_item.WorkItem", WorkItem.from_dict)

WORKER_NAME = "Worker_{}@{}".format(os.getpid(), socket.gethostname())


def factorise(n):
    """
    Simple algorithm to find the prime factors of the given number n
    :param n:
    :return:
    """

    def is_prime(n):
        return not any(x for x in range(2, int(sqrt(n)) + 1) if n % x == 0)

    primes = []
    candidates = range(2, n + 1)
    candidate = 2
    while not primes and candidate in candidates:
        if n % candidate == 0 and is_prime(candidate):
            primes = primes + [candidate] + factorise(n // candidate)
        candidate += 1
    return primes


def process(item):
    print("Factorising {} --> ".format(item.data))
    sys.stdout.flush()
    item.result = factorise(int(item.data))
    print(item.result)
    item.processed_by = WORKER_NAME


def main():
    dispatcher = Pyro4.core.Proxy("PYRONAME:distributed_ftp.dispatcher")
    print("This is worker {}".format(WORKER_NAME))
    print("getting work from dispatcher.")
    while True:
        try:
            item = dispatcher.get_work()
        except ValueError:
            print("No work available yet.")
        else:
            process(item)
            dispatcher.put_result(item)


if __name__ == "__main__":
    main()
