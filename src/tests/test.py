import glob
import os
import unittest

import cchardet

SKIP_LIST = [
    'tests/testdata/ja/utf-16le.txt',
    'tests/testdata/ja/utf-16be.txt',
    'tests/testdata/es/iso-8859-15.txt',
    'tests/testdata/da/iso-8859-1.txt',
    'tests/testdata/he/iso-8859-8.txt'
]


# Python can't decode encoding
SKIP_LIST_02 = [
    'tests/testdata/vi/viscii.txt',
    'tests/testdata/zh/euc-tw.txt'
]
SKIP_LIST_02.extend(SKIP_LIST)


class TestCChardet(unittest.TestCase):
    def test_ascii(self):
        detected_encoding = cchardet.detect(b'abcdefghijklmnopqrstuvwxyz')
        self.assertEqual('ascii', detected_encoding['encoding'].lower())

    def test_detect(self):
        testfiles = glob.glob('tests/testdata/*/*.txt')
        for testfile in testfiles:
            if testfile.replace("\\", "/") in SKIP_LIST:
                continue

            base = os.path.basename(testfile)
            expected_charset = os.path.splitext(base)[0]
            with open(testfile, 'rb') as f:
                msg = f.read()
                detected_encoding = cchardet.detect(msg)
                self.assertEqual(expected_charset.lower(), detected_encoding['encoding'].lower())

    def test_detector(self):
        detector = cchardet.UniversalDetector()
        with open("tests/samples/wikipediaJa_One_Thousand_and_One_Nights_SJIS.txt", 'rb') as f:
            line = f.readline()
            while line:
                detector.feed(line)
                if detector.done:
                    break
                line = f.readline()
        detector.close()
        detected_encoding = detector.result
        self.assertEqual("shift_jis", detected_encoding['encoding'].lower())

    def test_github_issue_20(self):
        """
        https://github.com/PyYoshi/cChardet/issues/20
        """
        msg = b'\x8f'

        cchardet.detect(msg)

        detector = cchardet.UniversalDetector()
        detector.feed(msg)
        detector.close()

    def test_decode(self):
        testfiles = glob.glob('tests/testdata/*/*.txt')
        for testfile in testfiles:
            if testfile.replace("\\", "/") in SKIP_LIST_02:
                continue

            base = os.path.basename(testfile)
            expected_charset = os.path.splitext(base)[0]
            with open(testfile, 'rb') as f:
                msg = f.read()
                detected_encoding = cchardet.detect(msg)
                try:
                    msg.decode(detected_encoding["encoding"])
                except LookupError as e:
                    print("LookupError: { file=%s, encoding=%s }" % (
                        testfile, detected_encoding["encoding"]))
                    raise e

    def test_utf8_with_bom(self):
        sample = b'\xEF\xBB\xBF'
        detected_encoding = cchardet.detect(sample)
        self.assertEqual("utf-8-sig", detected_encoding['encoding'].lower())

    def test_null_bytes(self):
        sample = b'ABC\x00\x80\x81'
        detected_encoding = cchardet.detect(sample)
        self.assertEqual(None, detected_encoding['encoding'])

    # def test_iso8859_2_csv(self):
    #     testfile = 'tests/samples/iso8859-2.csv'
    #     with open(testfile, 'rb') as f:
    #         msg = f.read()
    #         detected_encoding = cchardet.detect(msg)
    #         eq_(
    #             "iso8859-2",
    #             detected_encoding['encoding'].lower(),
    #             'Expected %s, but got %s' % (
    #                 "iso8859-2",
    #                 detected_encoding['encoding'].lower()
    #             )
    #         )
