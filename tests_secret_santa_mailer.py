import secret_santa_mailer
import unittest
from unittest.mock import patch
from urllib.error import HTTPError

class ContinueCheckerTests(unittest.TestCase):

    @patch("builtins.input", return_value="Y")
    def test_Yes(self, input):
        self.assertEqual(secret_santa_mailer.continue_checker("Message", "Exit Message"), None)


    @patch("builtins.input", return_value="N")
    def test_No(self, input):
        with self.assertRaises(SystemExit) as cm:
            secret_santa_mailer.continue_checker("Message", "Exit Message")
        self.assertEqual(cm.exception.code, "Exit Message")

class FindSantasTest(unittest.TestCase):

    def test_Dup_Emails(self):
        with patch.object(secret_santa_mailer, "continue_checker") as mock:
            secret_santa_mailer.find_santas(["C", "C"], {"A": "C", "B": "C"})
        mock.assert_called_with('Some reindeers are twins! [Duplicate email addresses]', 'Unexpectedly found twin reindeers! [Duplicate email addresses found]')


    def test_Miss_Names(self):
        with self.assertRaises(SystemExit) as cm:
            secret_santa_mailer.find_santas(["C", "D", "E"], {"A": "C", "B":"D"})
        self.assertEqual(cm.exception.code, "Mrs Claus says some Secret Santas is resting by the fireplace... [Missing 1 santa(s)]")


    def test_One_Name(self):
        with self.assertRaises(SystemExit) as cm:
            secret_santa_mailer.find_santas(["B"], {"A": "B"})
        self.assertEqual(cm.exception.code, "Not enough Secret Santas for the delivery! [Minimum of two Secret Santas required]")


    def test_Pass(self):
        self.assertEqual(secret_santa_mailer.find_santas(["D", "E", "F"], {"A": "D", "B": "E", "C": "F"}), None)

class FindReindeersTests(unittest.TestCase):

    def test_Dup_Names(self):
        with self.assertRaises(SystemExit) as cm:
            secret_santa_mailer.find_reindeers(["A", "A"], {"A": "B", "A":"C"})
        self.assertEqual(cm.exception.code, "There's an impostor! [All Secret Santas must be unique]")


    def test_Miss_Emails(self):
        with self.assertRaises(SystemExit) as cm:
            secret_santa_mailer.find_reindeers(["A", "B"], {"A": "C"})
        self.assertEqual(cm.exception.code, "There are reindeer resting in the barn... [Missing 1 email address(es)]")


    def test_Pass(self):
        self.assertEqual(secret_santa_mailer.find_reindeers(["A", "B", "C"], {"A": "D", "B": "E", "C": "F"}), None)


class CheckReindeersTest(unittest.TestCase):

    def test_Invalid(self):
        with self.assertRaises(SystemExit) as cm:
            secret_santa_mailer.check_reindeers({"A": "test@test.me", "B": "notanemailaddress.com"})
        self.assertEqual(cm.exception.code, "There are poorly reindeer at the vet's... [1 invalid email address(es)]")

    def test_Pass(self):
        self.assertEqual(secret_santa_mailer.check_reindeers({"A": "test@test.me", "B": "test@test.io"}), None)

class MimeGiphyTest(unittest.TestCase):

    def setUp(self):
        secret_santa_mailer.giphy_api_token = "Test"

    def test_Bad_Key(self):
        with self.assertRaises(HTTPError) as cm:
            secret_santa_mailer.mime_giphy()
        self.assertEqual(cm.exception.code, 403)

class SecretSantaRandomiserTest(unittest.TestCase):

    def test_Odd_Santas(self):
        sleighs = {"A": "D", "B": "E", "C": "F"}
        pairings = secret_santa_mailer.secret_santa_randomiser(sleighs)
        self.assertEqual(len(pairings.keys()), 3)
        self.assertEqual(len(pairings.values()), 3)
        self.assertEqual(set(sleighs.keys()) == set(pairings.keys()), True)
        self.assertEqual(set(sleighs.keys()) == set(pairings.values()), True)
        self.assertEqual(pairings.keys() != pairings.values(), True)

    def test_Even_Santas(self):
        sleighs = {"A": "E", "B": "F", "C": "G", "D": "H"}
        pairings = secret_santa_mailer.secret_santa_randomiser(sleighs)
        self.assertEqual(len(pairings.keys()), 4)
        self.assertEqual(len(pairings.values()), 4)
        self.assertEqual(set(sleighs.keys()) == set(pairings.keys()), True)
        self.assertEqual(set(sleighs.keys()) == set(pairings.values()), True)
        self.assertEqual(pairings.keys() != pairings.values(), True)

def suite():

    suite = unittest.TestSuite()

    test_classes = [ContinueCheckerTests, FindSantasTest, FindReindeersTests, CheckReindeersTest, MimeGiphyTest, SecretSantaRandomiserTest]

    for test_class in test_classes:
        suite.addTest(unittest.TestLoader().loadTestsFromTestCase(test_class))

    return suite

if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
