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
    * A TXT file for the plain text email body
    * A HTML file for the HTML email body

Example:
    To run this script execute:

        $ python secret_santa_mailer.py <<<EMAIL ADDRESS>>> <<<CSV FILENAME>>>
            <<<KEEP GIFS VALUE>>>

    where <<<EMAIL ADDRESS>>> is the outgoing Secret Santa Gmail mailbox, and
    <<<CSV FILENAME>>> is a CSV containing the Secret Santa names, and their
    email addresses. <<<KEEP GIFS VALUE>>> is optional; if it's set to 1, all
    GIFs that are embedded into the emails are saved locally, otherwise they are
    only temporarily stored until the emails have been generated.

Attributes:

"""
import getpass
import json
import imaplib
import os
import pandas as pd
import re
import secrets
import smtplib
import sys
import urllib.request
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import make_msgid


def continue_checker(message, exit_message):
    """Check that the code should continue to the next step

    Check that the code should continue to the next step, whilst displaying
    related messages.

    Args:
        message (str): Step-related message to display alongside the user input.
        exit_message (str): System exit message if the user chooses not to
            continue with the code

    Yields:
        Nothing if the user chooses to continue. If not, throws a relevant exit
        message, and then stops the code.
    """
    # Continue message for the user
    continue_flag = input(message + "\nDo you wish to continue? [Y/N]: ")

    # While the user hasn't entered an acceptable response, ask again
    while continue_flag.upper() not in ["Y", "N"]:
        continue_flag = input("Try again. Do you wish to continue? [Y/N]: ")

    # If the user has chosen not to continue, exit, and throw an error message
    if continue_flag.upper() == "N":
        sys.exit(exit_message)


def find_sleighs(santas, reindeers, sleighs):
    """Check enough Secret Santas, and reindeers were supplied

    Check that the number of Secret Santas [names] matches the number of
    reindeers [email address]. Check that the number of reindeer
    [email addresses] supplied matches the number of Secret Santas [names].

    Args:
        santas (list): List of Secret Santa names.
        reindeers (list): List of email addresses.
        sleighs (dict): Dictionary with names as keys, and email addresses as
            items. If everything is correct, items should match "reindeers".

    Yields:
        If there are duplicate Secret Santas, throw an error message. Give a
        message if there are duplicate email addresses. If there are fewer email
        addresses than names, each name missing an email address is printed,
        before exiting the system, and throwing an error message.  If there are
        fewer names than email addresses, exit the system, and throw an error
        message. If there are less than two Secret Santas, throw an error
        message. Otherwise, print statements that everything is okay.
    """
    # Check for duplicate names, and throw an error if there any duplicates
    if len(santas) != len(set(santas)):
        sys.exit("There's an impostor! [All Secret Santas must be unique]")

    # Check for duplicate messages, and ask the user if they want to continue
    if len(reindeers) != len(set(reindeers)):
        continue_checker("Some reindeers are twins! [Duplicate email " +
                         "addresses]", "Unexpectedly found twin reindeers! " +
                         "[Duplicate email addresses found]")

    # Difference calculation to see if there are missing names
    resting_santas = len(sleighs.keys()) - len(reindeers)

    # If there are missing names, or less than two names, throw an error message
    if resting_santas < 0:
        sys.exit("Mrs Claus says some Secret Santas is resting by the " +
                 "fireplace... [Missing " + str(abs(resting_santas)) +
                 " santa(s)]")
    elif len(sleighs.keys()) < 2:
        sys.exit("Not enough Secret Santas for the delivery! [Minimum of two " +
                 "Secret Santas required]")
    else:
        print("All Secret Santas present!")

    # Initialise a storage list to save names with missing email addresses
    resting_reindeers = []

    # Iterate through all names, and print any with missing email addresses
    for santa in santas:
        if santa not in sleighs:

            # Add names with missing email addresses to the storage list
            resting_reindeers.append(santa)

            # Print the names missing email addresses
            if re.search("[s]$", santa):
                print("The elves say " + santa + "' reindeer is resting in " +
                      "the barn... [Missing email address]")
            else:
                print("The elves say " + santa + "'s reindeer is resting in " +
                      "the barn... [Missing email address]")

    # If there are missing email address, throw an error message
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
    # Email validation regular expression
    vet_check = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"

    # Initialise a storage list for names with invalid email addresses
    poorly_reindeers = []

    # Iterate throw all names, and validate their email addresses
    for santa, reindeer in sleighs.items():
        if re.search(vet_check, reindeer) is None:

            # Add names with invalid email addresses to the storage list
            poorly_reindeers.append(santa)

            # Print a message for any names with invalid email addresses
            if re.search("[s]$", santa):
                print("The vet says " + santa + "' reindeer isn't feeling " +
                      "well... [Invalid email address]")
            else:
                print("The vet says " + santa + "'s reindeer isn't feeling " +
                      "well... [Invalid email address]")

    # Throw an error message if there are any invalid email addresses
    if len(poorly_reindeers) != 0:
        sys.exit("There are poorly reindeer at the vet's... [" +
                 str(len(poorly_reindeers)) + " invalid email address(es)]")
    else:
        print("All sleighs are ready to go!")


def mime_giphy():
    """Generate a MIME image from a random festive GIF from GIPHY

    Randomly download a festive GIF from GIPHY, create a corresponding MIME
    image with a unique content ID, and then delete the downloaded GIF.

    GIF is rated PG or below only, and GIPHY API use requires a token.

    Yields:
        Filename of the downloaded GIF that is stored in the working directory,
        and its GIPHY URL.
    """
    # Invoke the GIPHY API to get JSON for a random festive GIF
    giphy_url = ("http://api.giphy.com/v1/gifs/random?api_key=" +
                 giphy_api_token + "&tag=Merry+Christmas&rating=PG-13")

    # Open the URL, and decode the JSON return
    with urllib.request.urlopen(giphy_url) as giphy_request:
        giphy_data = json.loads(giphy_request.read())

    # Get the GIPHY URL
    giphy_link = giphy_data["data"]["fixed_height_downsampled_url"]

    # Get the GIPHY ID for the GIF
    giphy_id = giphy_data["data"]["id"]

    # Download the GIF to the local directory
    giphy_filename, _ = urllib.request.urlretrieve(giphy_link, "./images/" +
                                                   giphy_id + ".gif")

    # Open the GIF, and create a MIME image
    with open(giphy_filename, "rb") as gif:
        santas_picture = MIMEImage(gif.read())

    # Add a Content ID to santas_picture
    santas_picture.add_header("Content-ID", ("<" + giphy_id + ">"))

    # Delete the downloaded GIF - prevent storage of lots of GIFs at the end
    os.remove(giphy_filename) if not keep_gifs else None

    # Return both the downloaded filename, and the GIPHY URL
    return santas_picture, giphy_link, giphy_id


def secret_santa_randomiser(sleighs):
    """Check everyone's ready, randomly assign givers and receivers, and send
    out letters

    Check all entries are valid using other nested functions. Then randomly
    choose a Secret Santa, and randomly assign a gift receiver. Then use another
    nested function to email and notify the Secret Santa.

    Args:
        sleighs (dict): Dictionary with names as keys, and email addresses as
            items.
    Yields:
        santa_pairings (dict): Dictionary with giver names as keys, and email
            addresses as items.
    """
    # Initialise storage lists for the givers and receivers
    givers = []
    receivers = []

    # Iterate through all names until everyone is both giving and receiving
    while len(givers) < len(sleighs.keys()):

        # Randomly select a giver, and then add them to the storage list
        giver = secrets.choice([santa for santa in sleighs.keys()
                                if santa not in givers])
        givers.append(giver)

        # Check if the while loop is on the penultimate iteration. If this is
        # the case, only pick a receiver who was not a giver in previous
        # iterations. Prevents A>B, B>A, and C on their own. Otherwise, randomly
        # select a receiver.
        if len(givers) == len(sleighs.keys()) - 1 and giver in receivers:
            last_receivers = [santa for santa in sleighs.keys()
                              if santa not in receivers +
                              [giver, givers[receivers.index(giver)]]]
            if sorted(givers) == sorted(receivers + [last_receivers[0]]):
                receiver = last_receivers[1]
            else:
                receiver = last_receivers[0]
        else:
            receiver = secrets.choice([santa for santa in sleighs.keys()
                                       if santa not in receivers + [giver]])

        # Add the selected receiver to the storage list
        receivers.append(receiver)

    # Generate a dictionary of givers as keys, and receivers as items
    santa_pairings = dict(zip(givers, receivers))

    # Return a dictionary of givers as keys, and receivers as items
    return santa_pairings


def import_template(ext, path=".", enc=None):
    """Import the first files with a specific file extension in a given folder

    Find all the files in a folder with a specific file extension, e.g. ".txt",
    in a specific folder, return the first file found, and load it into the
    script.

    Args:
        ext (str): Extension of the filename required, e.g. ".txt" or ".html".
        path (str): Path to the folder where the file(s) are located, e.g.
            "./templates".
        enc (str): Encoding format used in the Python "open" built-in function.

    Yields:
        template_body (str): Imported file as desired.
    """
    # Get the first file with extension "ext" in the "path"
    template_filename = [template for template in os.listdir(path) if
                         template.endswith(ext)][0]

    # Import the template
    with open(path + "/" + template_filename, "r", encoding=enc) as f:
        template_body = f.read()

    # Return the imported file
    return template_body


def call_housekeeping(santas_mailbox, santas_letters):
    """Call housekeeping to tidy away all of Santa's letters

    Deletes the sent email messages to prevent anyone from finding out the
    Secret Santa pairings.

    Args:


    Yields:

    """
    # Assign the IMAP server, and log into it
    santas_server = imaplib.IMAP4_SSL("imap.gmail.com", 993)
    santas_server.login(santas_mailbox, santas_key)

    # Get a list of mailboxes, and select the Sent Mail
    santas_server.list()
    santas_server.select('"[Gmail]/Sent Mail"')

    # Iterate through each Message-ID, and flag it for deletion
    for santas_letter in santas_letters:
        typ, data = santas_server.search(None, 'HEADER MESSAGE-ID',
                                         santas_letter)
        for num in data[0].split():
            santas_server.store(num, '+FLAGS', '\\Deleted')

    # Expunge all emails flagged for deletion
    santas_server.expunge()

    # Close the IMAP server, and logout
    santas_server.close()
    santas_server.logout()


def call_postman(santas_mailbox, sleighs, santa_pairings):
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
        sleighs (dict): Dictionary with names as keys, and email addresses as
            items.
        santa_pairings (dict): Dictionary with giver names as keys, and email
            addresses as items.

    Yields:
        A sent email message for each Secret Santa, notifying them of their
        randomly assigned gift receiver.
    """
    # Initialise a storage list to hold all the unique message IDs for
    # subsequent deletion
    santas_letters = []

    # Get the plain text, and HTML email templates
    plain_body = import_template(".txt", "./templates")
    html_body = import_template(".html", "./templates", "utf8")

    # Extract the account, and domain names of the mailbox
    santas_account = re.search(r"(\w.+)@", santas_mailbox)[1]
    santas_domain = re.search(r"@(\w.+)", santas_mailbox)[1]

    # Open a connection to the email server, and send the email
    santas_server = smtplib.SMTP("smtp.gmail.com", 587)
    santas_server.ehlo()
    santas_server.starttls()
    santas_server.login(santas_mailbox, santas_key)

    # Iterate through each Secret Santa giver, and send them an email with
    # their selected receiver
    for giver in santa_pairings:

        # Extract the giver's email address, and their receiver
        giver_mailbox = sleighs[giver]
        receiver = santa_pairings[giver]

        # Get a random festive GIF using the GIPHY API in a MIME image format
        santas_picture, giphy_link, giphy_id = mime_giphy()

        # To ensure the HTML version is preferential, first setup a mixed MIME
        # message to contain the essentials, e.g. "From", "To", "Subject".
        # Then generate an alternative MIME subpart to hold plain text, and HTML
        # versions of the email. The plain text comes first to ensure HTML is
        # preferential.
        # As there is an embedded image in the HTML version, a related MIME
        # section is added that is a subpart of the alternative MIME subpart.
        # This ensures the HTML version is still preferential, and the embedded
        # image is displayed.

        # Initialise a mixed MIME message
        santas_letter = MIMEMultipart("mixed")

        # Attach required parts to the mixed part
        santas_letter["From"] = santas_mailbox
        santas_letter["To"] = giver_mailbox
        santas_letter["Subject"] = "Secret Santa"

        # Add a unique Message ID to the email, that incorporates
        # "santas-mailbox"
        santas_letter["Message-ID"] = make_msgid(idstring=santas_account,
                                                 domain=santas_domain)

        # Initialise an alternative subpart of the MIME message, and attach it
        santas_letter_alt = MIMEMultipart("alternative")
        santas_letter.attach(santas_letter_alt)

        # Attach plain text body to the alternative part
        santas_letter_alt.attach(MIMEText(plain_body.format(giver=giver,
                                                            receiver=receiver,
                                                            link=giphy_link),
                                          "plain"))

        # Initialise an related subpart of the alternative subpart of the MIME
        # message, and attach it
        santas_letter_rel = MIMEMultipart("related")
        santas_letter_alt.attach(santas_letter_rel)

        # Attach the HTML body, and santas_picture to the relative part
        santas_letter_rel.attach(MIMEText(html_body.format(giver=giver,
                                                           receiver=receiver,
                                                           link=giphy_link,
                                                           id=giphy_id),
                                          "html"))
        santas_letter_rel.attach(santas_picture)

        print("Sending letter to a Secret Santa...")

        # Send email to sender
        santas_server.sendmail(santas_mailbox, giver_mailbox,
                               santas_letter.as_string())

        # Append message ID to the storage list
        santas_letters.append(santas_letter["Message-ID"])

    # Exit server
    santas_server.quit()


def secret_santa_mailer(santas, reindeers, santas_mailbox):
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

    Yields:
        A sent email message for each Secret Santa, notifying them of their
        randomly assigned gift receiver.
    """
    # Create a dictionary of names and associated email addresses
    sleighs = dict(zip(secret_santas, secret_reindeers))

    # Run checks on the names and email addresses
    find_sleighs(santas, reindeers, sleighs)
    check_reindeers(sleighs)

    # Pair Secret Santas with each other randomly
    secret_santa_pairings = secret_santa_randomiser(sleighs)

    # Check that the user wants to send out the messages
    continue_checker("Secret Santa randomisation complete! Time to call the " +
                     "postman!", "OK, maybe next " + "time then!")

    # Send emails out to the giver notifying them of their receiver
    call_postman(santas_mailbox, sleighs, secret_santa_pairings)

    print("All letters sent - Merry Christmas!")


# Standalone program execution
if __name__ == '__main__':

    # Gmail account for the Secret Santa mailbox, with validator
    if re.search(r"(^[a-zA-Z0-9_.+-]+@gmail.com$)", sys.argv[1]) is None:
        sys.exit("Nobody's home... [Invalid Gmail address]")
    else:
        secret_santas_mailbox = sys.argv[1]

    # Import Secret Santas names, and their corresponding email addresses. Note
    # existing columns are forcibly renamed to "santas", and "reindeers", so
    # first column should have Secret Santa names, and second column should have
    # their email addresses
    secret_santa_sleighs = pd.read_csv(sys.argv[2],
                                       names=["santas", "reindeers"], header=0,
                                       skipinitialspace=True)
    secret_santas = secret_santa_sleighs.santas.tolist()
    secret_reindeers = secret_santa_sleighs.reindeers.tolist()

    # Strip any whitespace in the name or email address columns
    secret_santas = [santa.strip(' ') for santa in secret_santas]
    secret_reindeers = [reindeer.strip(' ') for reindeer in secret_reindeers]

    # See if the user wants to keep the downloaded GIFs from GIPHY
    try:
        keep_gifs = True if int(sys.argv[3]) == 1 else False
    except IndexError:
        keep_gifs = False

    # Obtain the password for the Secret Santa mailbox, and the GIPHY API token
    santas_key = getpass.getpass("Santa's secret key [Enter email password]: ")
    giphy_api_token = getpass.getpass(("Pick one of Santa's photo albums " +
                                       "[Enter GIPHY API token]: "))

    # Print messages to list all the loaded data, and then check to proceed
    print("Here's our Secret Santas:\n")
    print(pd.DataFrame({"1. Secret Santas": secret_santas,
                        "2. Email addresses": secret_reindeers}))
    continue_checker("All data loaded, ready to check the sleighs!", "Ok, " +
                     "maybe next time then!")

    # Execute function
    secret_santa_mailer(secret_santas
                        , secret_reindeers
                        , secret_santas_mailbox)
