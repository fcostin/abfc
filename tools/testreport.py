#! /usr/bin/env python
import argparse
import os.path
import sys


class Stats:
    def __init__(self, n_tests):
        self.n_tests = n_tests
        self.n_pass = 0
        self.n_fail = 0
        self.n_error = 0

    def handle_pass(self, test_result):
        self.n_pass +=1
        print 'PASS "%s"' % test_result

    def handle_fail(self, test_result):
        self.n_fail += 1
        print 'FAIL "%s"' % test_result

    def handle_error(self, test_result, msg):
        self.n_error += 1
        print 'ERROR "%s": %s' % (test_result, msg)

    def all_good(self):
        return self.n_tests == self.n_pass


def main():
    p = argparse.ArgumentParser()
    p.add_argument('test_results', nargs='*')
    args = p.parse_args()

    s = Stats(n_tests=len(args.test_results))
    for test_result in args.test_results:
        if os.path.exists(test_result):
            with open(test_result, 'r') as f:
                result = f.read().strip()
            if result == 'PASS':
                s.handle_pass(test_result)
            elif result == 'FAIL':
                s.handle_fail(test_result)
            else:
                s.handle_error(test_result, 'cannot understand test result file')
        else:
            s.handle_error(test_result, 'missing test result file')

    sys.exit(0 if s.all_good() else 1)

if __name__ == '__main__':
    main()

