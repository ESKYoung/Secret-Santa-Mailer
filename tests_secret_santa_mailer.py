"""Unit tests for Secret Santa double-blind mailer.

This module contains a unit tests for the various functions used in
secret_santa_mailer.py.

As the secret_santa_randomiser function makes random selections, the unittest
for this is deliberately run 10,000 times to ensure the function is operating
correctly.

Example:
    To run this script execute:

        $ python -m unittest tests_secret_santa_mailer

Attributes:

"""
import secret_santa_mailer
import unittest
from unittest.mock import patch
from urllib.error import HTTPError


class ContinueCheckerTests(unittest.TestCase):

    @patch("builtins.input", return_value="Y")
    def test_Yes(self, input):
        self.assertEqual(secret_santa_mailer.continue_checker("Message",
                                                              "Exit Message"),
                         None)

    @patch("builtins.input", return_value="N")
    def test_No(self, input):
        with self.assertRaises(SystemExit) as cm:
            secret_santa_mailer.continue_checker("Message", "Exit Message")
        self.assertEqual(cm.exception.code, "Exit Message")


class FindSantasTest(unittest.TestCase):

    def test_Dup_Emails(self):
        santas = ["A", "B"]
        reindeers = ["a", "a"]
        sleighs = dict(zip(santas, reindeers))
        with patch.object(secret_santa_mailer, "continue_checker") as mock:
            secret_santa_mailer.find_santas(reindeers, sleighs)
        mock.assert_called_with(("Some reindeers are twins! [Duplicate email " +
                                 "addresses]"), ("Unexpectedly found twin " +
                                 "reindeers! [Duplicate email addresses " +
                                 "found]"))

    def test_Miss_Names(self):
        santas = ["A", "B"]
        reindeers = ["a", "b", "c"]
        sleighs = dict(zip(santas, reindeers))
        with self.assertRaises(SystemExit) as cm:
            secret_santa_mailer.find_santas(reindeers, sleighs)
        self.assertEqual(cm.exception.code, ("Mrs Claus says some Secret " +
                                             "Santas is resting by the " +
                                             "fireplace... [Missing 1 " +
                                             "santa(s)]"))

    def test_One_Name(self):
        santas = ["A"]
        reindeers = ["a"]
        sleighs = dict(zip(santas, reindeers))
        with self.assertRaises(SystemExit) as cm:
            secret_santa_mailer.find_santas(reindeers, sleighs)
        self.assertEqual(cm.exception.code, ("Not enough Secret Santas for " +
                                             "the delivery! [Minimum of two " +
                                             "Secret Santas required]"))

    def test_Pass(self):
        santas = ["A", "B", "C"]
        reindeers = ["a", "b", "c"]
        sleighs = dict(zip(santas, reindeers))
        self.assertEqual(secret_santa_mailer.find_santas(reindeers, sleighs),
                         None)


class FindReindeersTests(unittest.TestCase):

    def test_Dup_Names(self):
        santas = ["A", "A"]
        reindeers = ["a", "b"]
        sleighs = dict(zip(santas, reindeers))
        with self.assertRaises(SystemExit) as cm:
            secret_santa_mailer.find_reindeers(santas, sleighs)
        self.assertEqual(cm.exception.code, ("There's an impostor! [All " +
                         "Secret Santas must be unique]"))

    def test_Miss_Emails(self):
        santas = ["A", "B"]
        reindeers = ["a"]
        sleighs = dict(zip(santas, reindeers))
        with self.assertRaises(SystemExit) as cm:
            secret_santa_mailer.find_reindeers(santas, sleighs)
        self.assertEqual(cm.exception.code, ("There are reindeer resting in " +
                         "the barn... [Missing 1 email address(es)]"))

    def test_Pass(self):
        santas = ["A", "B", "C", "D"]
        reindeers = ["a", "b", "c", "d"]
        sleighs = dict(zip(santas, reindeers))
        self.assertEqual(secret_santa_mailer.find_reindeers(santas, sleighs),
                         None)


class CheckReindeersTest(unittest.TestCase):

    def test_Invalid(self):
        santas = ["A", "B"]
        reindeers = ["test@test.me", "test.invalid.com"]
        sleighs = dict(zip(santas, reindeers))
        with self.assertRaises(SystemExit) as cm:
            secret_santa_mailer.check_reindeers(sleighs)
        self.assertEqual(cm.exception.code, ("There are poorly reindeer at " +
                         "the vet's... [1 invalid email address(es)]"))

    def test_Pass(self):
        santas = ["A", "B"]
        reindeers = ["test@test.me", "test@test.io"]
        sleighs = dict(zip(santas, reindeers))
        self.assertEqual(secret_santa_mailer.check_reindeers(sleighs), None)


class MimeGiphyTest(unittest.TestCase):

    def setUp(self):
        secret_santa_mailer.giphy_api_token = "Test"

    def test_Bad_Key(self):
        with self.assertRaises(HTTPError) as cm:
            secret_santa_mailer.mime_giphy()
        self.assertEqual(cm.exception.code, 403)


class SecretSantaRandomiserTest(unittest.TestCase):

    def test_Odd_Santas(self):
        santas = ["A", "B", "C", "D", "E"]
        reindeers = ["a", "b", "c", "d", "e"]
        sleighs = dict(zip(santas, reindeers))
        for i in range(9999):
            pairings = secret_santa_mailer.secret_santa_randomiser(sleighs)
            self.assertEqual(len(pairings.keys()), 5)
            self.assertEqual(len(pairings.values()), 5)
            self.assertEqual(set(sleighs.keys()) == set(pairings.keys()), True)
            self.assertEqual(set(sleighs.keys()) == set(pairings.values()),
                             True)
            self.assertEqual(pairings.keys() != pairings.values(), True)

    def test_Even_Santas(self):
        santas = ["A", "B", "C", "D", "E", "F"]
        reindeers = ["a", "b", "c", "d", "e", "f"]
        sleighs = dict(zip(santas, reindeers))
        for i in range(9999):
            pairings = secret_santa_mailer.secret_santa_randomiser(sleighs)
            self.assertEqual(len(pairings.keys()), 6)
            self.assertEqual(len(pairings.values()), 6)
            self.assertEqual(set(sleighs.keys()) == set(pairings.keys()), True)
            self.assertEqual(set(sleighs.keys()) == set(pairings.values()),
                             True)
            self.assertEqual(pairings.keys() != pairings.values(), True)


class ImportTemplateTest(unittest.TestCase):

    def test_future(self):
        pass



class CallPostmanTest(unittest.TestCase):

    def test_future(self):
        pass


class SecretSantaMailerTest(unittest.TestCase):

    def test_future(self):
        pass


def gen_tests_suite():

    tests_suite = unittest.TestSuite()

    test_classes = [ContinueCheckerTests
                    , FindSantasTest
                    , FindReindeersTests
                    , CheckReindeersTest
                    , MimeGiphyTest
                    , SecretSantaRandomiserTest
                    , ImportTemplateTest
                    , CallPostmanTest]

    for test_class in test_classes:

        test_loader = unittest .TestLoader()

        tests_suite.addTest(test_loader.loadTestsFromTestCase(test_class))

    return tests_suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(gen_tests_suite())
