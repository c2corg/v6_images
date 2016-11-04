import sys
import argparse
import datetime
import queue
import threading
import traceback

import logging
log = logging.getLogger(__name__)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(levelname)s - %(message)s')
ch.setFormatter(formatter)
log.addHandler(ch)


class Worker(threading.Thread):

    def __init__(self, queue, method):
        threading.Thread.__init__(self)
        self.queue = queue
        self.method = method

    def run(self):
        while True:
            item = self.queue.get()
            if item is None:
                break
            self.method(item)
            self.queue.task_done()


class MultithreadProcessor():

    @staticmethod
    def argument_parser():
        parser = argparse.ArgumentParser()
        parser.add_argument(
            '-f', '--force', dest='force',
            action='store_const', const=True, default=False,
            help='Force processing of existing images.')
        parser.add_argument(
            '-j', '--jobs', type=int, dest='jobs', default=5,
            help='Number of consumer jobs.')
        parser.add_argument(
            '-k', '--key', dest='key', default=None,
            help='Process only one key.')
        parser.add_argument(
            '-l', '--limit', type=int, dest='limit', default=None,
            help='Limit the number of original images to process.')
        parser.add_argument(
            '-v', '--verbose', dest='verbose',
            action='store_const', const=True, default=False,
            help='Increase verbosity')
        return parser

    @classmethod
    def run(cls, argv=sys.argv):
        parser = cls.argument_parser()
        args = vars(parser.parse_args(argv[1:]))
        processor = cls()
        processor.execute(**args)

    def execute(self, force=False, jobs=5, limit=None, verbose=False,
                timeout=None, key=None, **kwargs):
        self.force = force
        self.timeout = timeout
        self.key = key

        if verbose:
            log.setLevel(logging.DEBUG)
        else:
            log.setLevel(logging.INFO)

        self.skipped = 0
        self.processed = 0
        self.errors = 0
        self.start = datetime.datetime.now()

        self.queue = queue.Queue()
        self.workers = []
        self.lock = threading.Lock()

        for i in range(0, jobs):
            worker = Worker(self.queue, self.process_key)
            worker.start()
            self.workers.append(worker)

        self.total = 0
        for key in self.keys():
            self.total += 1

            self.queue.put(key)

            if limit is not None and self.total >= limit:
                break

        # block until all keys are processed
        self.queue.join()

        # stop workers
        for worker in self.workers:
            self.queue.put(None)
        for worker in self.workers:
            worker.join()

        print('Images: {}, skipped: {}, processed: {}, errors: {}'.
              format(self.total, self.skipped, self.processed, self.errors))
        print('Total duration: {}'.format(datetime.datetime.now() - self.start))

    def keys(self):
        if self.key is not None:
            yield self.key
        else:
            for key in self.do_keys():
                yield key

    def do_keys(self):
        raise NotImplementedError()

    def process_key(self, key):
        try:
            self.do_process_key(key)
        except Exception:
            # continue on errors
            log.error("{}\n{}".format(key, traceback.format_exc()))
            with self.lock:
                self.errors += 1
        progress = self.skipped + self.processed + self.errors
        if progress % 10 == 0:
            log.info('Progress: {} / {} ({:.2%}), elapsed time: {}'.
                     format(progress,
                            self.total,
                            progress / self.total,
                            datetime.datetime.now() - self.start))

    def do_process_key(self):
        raise NotImplementedError()
