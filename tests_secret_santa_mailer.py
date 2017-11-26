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
    """Unit tests for the continue_checker function"""

    @patch("builtins.input", return_value="Y")
    def test_Yes(self, input):
        """Check user inputs

        If the user enters "Y", nothing should happen.
        """
        self.assertEqual(secret_santa_mailer.continue_checker("Message",
                                                              "Exit Message"),
                         None)

    @patch("builtins.input", return_value="N")
    def test_No(self, input):
        """Check user inputs

        If the user enters "N", a SystemExit should be returned, with the
        appropriate exit message.
        """
        with self.assertRaises(SystemExit) as cm:
            secret_santa_mailer.continue_checker("Message", "Exit Message")
        self.assertEqual(cm.exception.code, "Exit Message")


class FindSleighsTest(unittest.TestCase):
    """Unit tests for the find_sleighs function"""

    def test_Dup_Names(self):
        """Check for duplicate names

        Check a SystemExit and appropriate exit message are shown if there are
        duplicate names."""
        santas = ["A", "A"]
        reindeers = ["a", "b"]
        sleighs = dict(zip(santas, reindeers))
        with self.assertRaises(SystemExit) as cm:
            secret_santa_mailer.find_sleighs(santas, reindeers, sleighs)
        self.assertEqual(cm.exception.code, ("There's an impostor! [All " +
                                             "Secret Santas must be unique]"))

    def test_Dup_Emails(self):
        """Check for duplicate email addresses

        Check a print message is shown if duplicate email addresses were
        inputted. """
        santas = ["A", "B"]
        reindeers = ["a", "a"]
        sleighs = dict(zip(santas, reindeers))
        with patch.object(secret_santa_mailer, "continue_checker") as mock:
            secret_santa_mailer.find_sleighs(santas, reindeers, sleighs)
        mock.assert_called_with(("Some reindeers are twins! [Duplicate email " +
                                 "addresses]"), ("Unexpectedly found twin " +
                                                 "reindeers! [Duplicate " +
                                                 "email addresses found]"))

    def test_Miss_Names(self):
        """Check for missing names

        Check a SystemExit and appropriate exit message are shown if there are
        missing names."""
        santas = ["A", "B"]
        reindeers = ["a", "b", "c"]
        sleighs = dict(zip(santas, reindeers))
        with self.assertRaises(SystemExit) as cm:
            secret_santa_mailer.find_sleighs(santas, reindeers, sleighs)
        self.assertEqual(cm.exception.code, ("Mrs Claus says some Secret " +
                                             "Santas is resting by the " +
                                             "fireplace... [Missing 1 " +
                                             "santa(s)]"))

    def test_One_Name(self):
        """Check for only one name

        Check a SystemExit and appropriate exit message are shown if only one
        Secret Santa was inputted."""
        santas = ["A"]
        reindeers = ["a"]
        sleighs = dict(zip(santas, reindeers))
        with self.assertRaises(SystemExit) as cm:
            secret_santa_mailer.find_sleighs(santas, reindeers, sleighs)
        self.assertEqual(cm.exception.code, ("Not enough Secret Santas for " +
                                             "the delivery! [Minimum of two " +
                                             "Secret Santas required]"))

    def test_Miss_Emails(self):
        """Check for missing email addresses

        Check a SystemExit and appropriate exit message are shown if there are
        missing email addresses."""
        santas = ["A", "B", "C"]
        reindeers = ["a", "b"]
        sleighs = dict(zip(santas, reindeers))
        with self.assertRaises(SystemExit) as cm:
            secret_santa_mailer.find_sleighs(santas, reindeers, sleighs)
        self.assertEqual(cm.exception.code, ("There are reindeer resting in " +
                                             "the barn... [Missing 1 email " +
                                             "address(es)]"))

    def test_Pass(self):
        """Check the function passes normally

            Check the function passes normally."""
        santas = ["A", "B", "C"]
        reindeers = ["a", "b", "c"]
        sleighs = dict(zip(santas, reindeers))
        self.assertEqual(secret_santa_mailer.find_sleighs(santas, reindeers,
                                                          sleighs), None)


class CheckReindeersTest(unittest.TestCase):
    """Unit tests for the check_reindeers function"""

    def test_Invalid(self):
        """Check for invalid email addresses

        Check a SystemExit and appropriate exit message are shown if there are
        invalid email addresses."""
        santas = ["A", "B"]
        reindeers = ["test@test.me", "test.invalid.com"]
        sleighs = dict(zip(santas, reindeers))
        with self.assertRaises(SystemExit) as cm:
            secret_santa_mailer.check_reindeers(sleighs)
        self.assertEqual(cm.exception.code, ("There are poorly reindeer at " +
                                             "the vet's... [1 invalid email " +
                                             "address(es)]"))

    def test_Pass(self):
        """Check the function passes normally

        Check the function passes normally."""
        santas = ["A", "B"]
        reindeers = ["test@test.me", "test@test.io"]
        sleighs = dict(zip(santas, reindeers))
        self.assertEqual(secret_santa_mailer.check_reindeers(sleighs), None)


class MimeGiphyTest(unittest.TestCase):
    """Unit tests for the mime_giphy function"""

    def setUp(self):
        """Set up a fake GIPHY API token"""
        secret_santa_mailer.giphy_api_token = "Test"

    def test_Bad_Key(self):
        """Check the URL request

        Check for a HTTP 403 error when a bad GIPHY API token is submitted."""
        with self.assertRaises(HTTPError) as cm:
            secret_santa_mailer.mime_giphy()
        self.assertEqual(cm.exception.code, 403)


class SecretSantaRandomiserTest(unittest.TestCase):
    """Unit tests for the secret_santa_randomiser function"""

    def test_Odd_Santas(self):
        """Check function runs with an odd number of Secret Santas

        Test function with odd number of Secret Santas, looping over 10,000
        times to ensure randomisation process operates correctly."""
        santas = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", 
                  "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", 
                  "Y"]
        reindeers = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", 
                     "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", 
                     "w", "x", "y"]
        sleighs = dict(zip(santas, reindeers))
        for i in range(9999):
            pairings = secret_santa_mailer.secret_santa_randomiser(sleighs)
            self.assertEqual(len(pairings.keys()), 25)
            self.assertEqual(len(pairings.values()), 25)
            self.assertEqual(set(sleighs.keys()) == set(pairings.keys()), True)
            self.assertEqual(set(sleighs.keys()) == set(pairings.values()),
                             True)
            self.assertEqual(pairings.keys() != pairings.values(), True)

    def test_Even_Santas(self):
        """Check function runs with an even number of Secret Santas

        Test function with even number of Secret Santas, looping over 10,000
        times to ensure randomisation process operates correctly."""
        santas = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", 
                  "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", 
                  "Y", "Z"]
        reindeers = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", 
                     "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", 
                     "w", "x", "y", "z"]
        sleighs = dict(zip(santas, reindeers))
        for i in range(9999):
            pairings = secret_santa_mailer.secret_santa_randomiser(sleighs)
            self.assertEqual(len(pairings.keys()), 26)
            self.assertEqual(len(pairings.values()), 26)
            self.assertEqual(set(sleighs.keys()) == set(pairings.keys()), True)
            self.assertEqual(set(sleighs.keys()) == set(pairings.values()),
                             True)
            self.assertEqual(pairings.keys() != pairings.values(), True)


class ImportTemplateTest(unittest.TestCase):
    """Unit tests for the import_template function"""

    def test_future(self):
        pass


class CallPostmanTest(unittest.TestCase):
    """Unit tests for the call_postman function"""

    def test_future(self):
        pass


class SecretSantaMailerTest(unittest.TestCase):
    """Unit tests for the secret_santa_mailer function"""

    def test_future(self):
        pass


def gen_tests_suite():
    """Create a suite of unit tests

    Add all unit tests into a unit test suite to run later"""

    # Initialise a unit test suite
    tests_suite = unittest.TestSuite()

    # Create a list of all unit test classes
    test_classes = [ContinueCheckerTests,
                    FindSleighsTest,
                    CheckReindeersTest,
                    MimeGiphyTest,
                    SecretSantaRandomiserTest,
                    ImportTemplateTest,
                    CallPostmanTest,
                    SecretSantaMailerTest]

    # Iterate through each unit test class, and load it into the unit test suite
    for test_class in test_classes:
        test_loader = unittest.TestLoader()
        tests_suite.addTest(test_loader.loadTestsFromTestCase(test_class))

    return tests_suite


# Execute the unit test suite
if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(gen_tests_suite())
