"""Secret Santa double-blind mailer.

This module randomly assigns Secret Santas to each other, so that one gives a
gift to another.

The randomisation is double-blind, as both the giver and receiver are randomly
selected by this Python module without knowledge by the programmer.

Secret Santas are emailed their assigned person directly, as this module
connects to a Gmail account. The emails are supplied in both plain text and HTML
formats, with a festive GIF (PG-rated) embedded in the latter.

The module requires:
    * A two-column CSV file of Secret Santa names, and their email addresses
    * A TXT file for the plain text email body, named
      "Secret_Santa_Email_Body.txt"
    * A HTML file for the HTML email body, named "Secret_Santa_Email_Body.html"

Example:
    To run this script execute:
        $ python secret_santa_mailer.py <email address> <input file>
    where <email address> is the Secret Santa Gmail mailbox, and <input file>
    is a CSV containing the Secret Santa names, and their email addresses.

Attributes:

"""
import sys
import pandas as pd
import secrets
import re
import smtplib
import urllib.request
import json
import getpass
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage


def find_santas(reindeers, sleighs):
    """Check enough Secret Santas were supplied

    Check that the number of Secret Santas [names] matches the number of
    reindeers [email address].

    Args:
        reindeers (list): List of email addresses.
        sleighs (dict): Dictionary with names as keys, and email addresses as
            items. If everything is correct, items should match "reindeers".

    Yields:
        If there are fewer names than email addresses, exit the system, and
        throw an error message. Otherwise, print a statement that everything is
        okay.
    """
    resting_santas = len(sleighs.keys()) - len(reindeers)
    if resting_santas < 0:
        sys.exit("Mrs Claus says some Secret Santas is resting by the " +
                 "fireplace... [Missing " + str(abs(resting_santas)) +
                 " santa(s)]")
    elif len(sleighs.keys()) < 2:
        sys.exit("Not enough Secret Santas for the delivery! [Minimum of two " +
                "Secret Santas required]")
    else:
        print("All Secret Santas present!")


def find_reindeers(santas, sleighs):
    """Check enough reindeers were supplied

    Check that the number of reindeer [email adresses] supplied matches the
    number of Secret Santas [names].

    Args:
        santas (list): List of Secret Santa names.
        sleighs (dict): Dictionary with names as keys, and email addresses as
            items. If everything is correct, keys should match "santas".

    Yields:
        If there are fewer email addresses than names, each name missing an
        email address is printed, before exiting the system, and throwing an
        error message. Otherwise, print a statement that everything is okay.
    """
    resting_reindeers = []

    for santa in santas:
        if santa not in sleighs:

            resting_reindeers.append(santa)

            if re.search("[s]$", santa):
                elves_report = ("The elves say " + santa + "' reindeer is " +
                                "resting in the barn... [Missing email " +
                                "address]")
            else:
                elves_report = ("The elves say " + santa + "'s reindeer is " +
                                "resting in the barn... [Missing email " +
                                "address]")

            print(elves_report)

    if len(resting_reindeers) != 0:
        sys.exit("There are reindeer resting in the barn... [Missing " +
                 str(len(resting_reindeers)) + " email address(es)]")
    else:
        print("All reindeers present!")


def check_reindeers(sleighs):
    """Check that the reindeers are all healthy

    Check that each of the reindeer are healthy, i.e. check valid email
    addresses have been supplied. Uses regex to validate these email addresses.

    Args:
        sleighs (dict): Dictionary with names as keys, and email addresses as
            items.

    Yields:
        If there are invalid email address, the corresponding name, then exit
        the system, and throw an error message. Otherwise, print a statement
        that everything is okay.
    """
    # Email validation regex
    vet_check = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"

    poorly_reindeers = []

    for santa, reindeer in sleighs.items():
        if re.search(vet_check, reindeer) is None:

            poorly_reindeers.append(santa)

            if re.search("[s]$", santa):
                vet_report = ("The vet says " + santa + "' reindeer isn't " +
                              "feeling well... [Invalid email address]")
            else:
                vet_report = ("The vet says " + santa + "'s reindeer isn't " +
                              "feeling well... [Invalid email address]")

            print(vet_report)

    if len(poorly_reindeers) != 0:
        sys.exit("There are poorly reindeer at the vet's... [" +
                 str(len(poorly_reindeers)) + " invalid email address(es)]")
    else:
        print("All sleighs are ready to go!")


def get_giphy():
    """Get a random festive GIF from GIPHY

    Randomly download a festive GIF from GIPHY. Rated PG or below only, and
    requires a GIPHY API token.

    Yields:
        Filename of the downloaded GIF that is stored in the working directory,
        and its GIPHY URL.
    """
    giphy_url = ("http://api.giphy.com/v1/gifs/random?api_key=" +
                 giphy_api_token + "&tag=Christmas&rating=PG")

    with urllib.request.urlopen(giphy_url) as giphy_request:
        giphy_data = json.loads(giphy_request.read())

    giphy_link = giphy_data["data"]["fixed_height_downsampled_url"]

    giphy_filename, _ = urllib.request.urlretrieve(giphy_link, "image.gif")

    return giphy_filename, giphy_link


def call_postman(santas_mailbox, giver, giver_mailbox, receiver, plain_body,
                 html_body):
    """Call the postman, and post Santa's instructions to all Secret Santas

    Generate an email message based on the plain text, and HTML templates.
    Populate this message with the randomly-assigned receiver's name, the
    random, festive GIF and its link.

    Then email this to the randomly selected Secret Santa using a Gmail account.
    Requires Gmail account, and password. Account must be set to allow less
    secure apps, or, if using two-step verification, an app password must be
    used instead.

    Args:
        santas_mailbox (str): A valid email address corresponding to the Gmail
            account.
        giver (str): Randomly selected Secret Santa.
        giver_mailbox (str): A valid email address for "giver".
        receiver (str): Randomly assigned gift receiver from the "giver".
        plain_body (str): Plain text email message template.
        html_body (str): HTML email message template.

    Yields:
        A sent email message for each Secret Santa, notifying them of their
        randomly assigned gift receiver.
    """
    giphy_filename, giphy_link = get_giphy()

    santas_letter = MIMEMultipart("related")
    santas_letter["Subject"] = "Secret Santa"
    santas_letter["From"] = santas_mailbox
    santas_letter["To"] = giver_mailbox
    santas_letter.preamble = "This is a multi-part message in MIME format."

    santas_letter_alt = MIMEMultipart("alternative")
    santas_letter.attach(santas_letter_alt)

    santas_letter.attach(MIMEText(plain_body.format(giver=giver,
                                                    receiver=receiver,
                                                    link=giphy_link), "plain"))
    santas_letter_alt.attach(MIMEText(html_body.format(giver=giver,
                                                       receiver=receiver,
                                                       link=giphy_link),
                                      "html"))

    with open(giphy_filename, "rb") as gif:
        santas_picture = MIMEImage(gif.read())

    santas_picture.add_header("Content-ID", "<image1>")
    santas_letter.attach(santas_picture)

    print("Sending letter to a Secret Santa...")

    santas_server = smtplib.SMTP("smtp.gmail.com", 587)
    santas_server.ehlo()
    santas_server.starttls()
    santas_server.login(santas_mailbox, santas_key)
    santas_server.sendmail(santas_mailbox, giver_mailbox,
                           santas_letter.as_string())
    santas_server.quit()


def secret_santa_mailer(santas, reindeers, santas_mailbox, plain_body,
                        html_body):
    """Check everyone's ready, randomly assign givers and receivers, and send
    out letters

    Check all entries are valid using other nested functions. Then randomly
    choose a Secret Santa, and randomly assign a gift receiver. Then use another
    nested function to email and notify the Secret Santa.

    Args:
        santas (list): List of Secret Santa names.
        reindeers (list): List of email addresses.
        santas_mailbox (str): A valid email address corresponding to the Gmail
            account.
        plain_body (str): Plain text email message template.
        html_body (str): HTML email message template.

    Yields:
        A sent email message for each Secret Santa, notifying them of their
        randomly assigned gift receiver.
    """
    sleighs = dict(zip(secret_santas, secret_reindeers))

    find_santas(reindeers, sleighs)
    find_reindeers(santas, sleighs)
    check_reindeers(sleighs)

    givers = []
    receivers = []

    # Boolean flag to check for an odd number of Secret Santas
    odd_santa_flag = len(sleighs.keys()) % 2 != 0

    while len(givers) < len(sleighs.keys()):

        giver = secrets.choice([santa for santa in sleighs.keys()
                                if santa not in givers])
        givers.append(giver)

        """ Check if there are an odd number of Secret Santas, and the while
        loop is on the penultimate iteration. If this is the case, only pick a
        receiver who was not a giver in previous iterations. Prevents A>B, B>A,
        and C on their own."""
        if odd_santa_flag and len(givers) == len(sleighs.keys()) - 1 \
                and giver in receivers:
            receiver = [santa for santa in sleighs.keys()
                        if santa not in receivers +
                        [giver, givers[receivers.index(giver)]]][0]
        else:
            receiver = secrets.choice([santa for santa in sleighs.keys()
                                       if santa not in receivers + [giver]])
        
        receivers.append(receiver)
        
        call_postman(santas_mailbox, giver, sleighs[giver], receiver,
                     plain_body, html_body)

    print("All letters sent - Merry Christmas!")


# Import the plain text email message template
with open("Secret_Santa_Email_Body.txt", "r") as f:
    santa_letter_plain = f.read()

# Import the HTML email message template
with open("Secret_Santa_Email_Body.html", "r", encoding="utf8") as f:
    santa_letter_html = f.read()

# Gmail account for the Secret Santa mailbox, with validator
if re.search(r"(^[a-zA-Z0-9_.+-]+@gmail.com$)", sys.argv[1]) is None:
    sys.exit("Nobody's home... [Invalid Gmail address]")
else:
    secret_santas_mailbox = sys.argv[1]

# Import Secret Santas and their reindeers
secret_santa_sleighs = pd.read_csv(sys.argv[2],
                                   names=["santas", "reindeers"], header=0)
secret_santas = secret_santa_sleighs.santas.tolist()
secret_reindeers = secret_santa_sleighs.reindeers.tolist()

""" Set Santa's key(Gmail account password), and the GIPHY API token as global
variables"""
global santas_key
global giphy_api_token

# Get Santa's key, and the GIPHY API token
santas_key = getpass.getpass("Santa's secret key [Enter email password]: ")
giphy_api_token = getpass.getpass(("Pick one of Santa's photo albums " +
                                   "[Enter GIPHY API token]: "))

# Execute function
secret_santa_mailer(secret_santas
                    , secret_reindeers
                    , secret_santas_mailbox
                    , santa_letter_plain
                    , santa_letter_html)
