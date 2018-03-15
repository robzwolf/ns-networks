import random
import sys
import Pyro4
from Pyro4.util import SerializerBase
from work_item import WorkItem

# For "work_item.WorkItem" we register a deserialisation hook to be able to get these back from Pyro
SerializerBase.register_dict_to_class("work_item.WorkItem", WorkItem.from_dict)

NUMBER_OF_ITEMS = 40


def main():
    print("This program will calculate prime factors of a bunch of random numbers.")
    print("The more workers you will start on different cores, the faster you will get the complete list of results!")
    with Pyro4.core.Proxy("PYRONAME:distributed_ftp.dispatcher") as dispatcher:
        place_work(dispatcher)
        numbers = collect_results(dispatcher)
    print_results(numbers)


def place_work(dispatcher):
    print("Placing work items into dispatcher queue.")
    for i in range(NUMBER_OF_ITEMS):
        number = random.randint(3211, 4999999) * random.randint(3211, 999999)
        item = WorkItem(i + 1, number)
        dispatcher.put_work(item)


def collect_results(dispatcher):
    print("Getting results from dispatcher queue.")
    numbers = {}
    while len(numbers) < NUMBER_OF_ITEMS:
        try:
            item = dispatcher.get_result()
        except ValueError:
            print("Not all results available yet (got {} out of {}). Work queue size: {}"
                  .format(len(numbers), NUMBER_OF_ITEMS, dispatcher.work_queue_size()))
        else:
            print("Got result: {} (from {})".format(item, item.processed_by))
            numbers[item.data] = item.result

    if dispatcher.result_queue_size() > 0:
        print("There's still stuff in the dispatcher result queue, that's odd...")
    return numbers


def print_results(numbers):
    print("Computed prime factors follow:")
    for (number, factorials) in numbers.items():
        print("{} --> {}".format(number, factorials))


if __name__ == "__main__":
    main()
