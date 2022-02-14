#!/usr/bin/env python3

import unittest

import spider

class TestCrackUrl(unittest.TestCase):
    def test_three(self):
        self.assertEqual(spider.crack_url(r"http://fake.com:99/path/file.htm"),
                         spider.URLParts(protocol="http://",
                                         hostport="fake.com:99",
                                         path="/path/file.htm"))

    def test_noproto(self):
        self.assertEqual(spider.crack_url(r"fake.com:99/path/file.htm"),
                         spider.URLParts(protocol=None,
                                         hostport="fake.com:99",
                                         path="/path/file.htm"))

    def test_nohost(self):
        self.assertEqual(spider.crack_url(r"path/file.htm"),
                         spider.URLParts(protocol=None,
                                         hostport=None,
                                         path="path/file.htm"))


if __name__ == "__main__":
    unittest.main()
