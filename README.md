# Secret Santa Mailer :santa:

Double-blind random selection to pair a list of Secret Santas with each other. Each Secret Santa is emailed their randomly-selected gift recipient directly.

## Getting started

Here's how to get the Secret Santa Mailer up and running on your system.

### Prerequisites

You need the following to run this code:

1. Python 3 either through command line or your favourite IDE;
2. The ``pandas`` module;
3. Local clone of this repository;
4. ``.csv`` file with Secret Santas' names and emails &dagger;;
  * Add a header row - any will do!
  * Add data from Row 2 onwards
  * First column should have **unique** Secret Santa names
  * Second column should have their email address - *duplicates are allowed*
5. Access to a suitably festive mailbox; and
6. A GIPHY API token &mdash; get one [here](https://developers.giphy.com)!

&dagger; Use the repo's [template](templates/Secret_Santa_Template.csv) if you'd like!

### Running the code

Navigate to your local repository using command line or your Python IDE, then run this code:

~~~
python secret_santa_mailer.py <<<EMAIL ADDRESS>> <<<CSV FILENAME>>>
~~~

where ``<<<EMAIL ADDRESS>>>`` is a valid mailbox from where emails are sent to each Secret Santa, and ``<<<CSV FILENAME>>>`` is the ``.csv`` file from Step 4, including the full path if it's not in your working directory.

## How it works

Here's how the code works:

1. Checks that the outgoing email address is valid;
2. Loads the ``.csv`` file containing Secret Santa details;
3. Splits out names, and email addresses from Step 2;
4. Requests outgoing email address password, and GIPHY API token; and
5. Executes ``secret_santa_mailer`` function.

### ``secret_santa_mailer`` function

The ``secret_santa_mailer`` parent function works as follows:

1. ``find_santas`` and ``find_reindeers`` check enough names, and email addresses were supplied;
  * Minimum of two names required, otherwise throws an error
  * Must be unique names, otherwise throws an error
  * Prints names that are missing email addresses, then throws an error
  * Email addresses can be duplicate, but a continuation message will be printed
2. ``check_reindeers`` ensures email addresses are valid;
  * Prints names with invalid email addresses, then throws an error
3. ``secret_santa_pairings`` randomly pairs Secret Santas with each other; and
  * A giver is random selected, and is paired with a random selected receiver
  * A giver's receiver cannot be themselves
  * [*Bear with me*] If there are an odd number of Secret Santas, the penultimate giver cannot be assigned a receiver who is already giving them a gift, for example:
    * Suppose there are three Secret Santas, ``A``, ``B``, and ``C``
    * If ``A`` pairs with ``B``, then ``B`` **must** pair with ``C``, leaving ``C`` to pair with ``A`` &mdash; this is what this function does
    * Otherwise, there's a chance ``B`` pairs with ``A``, leaving ``C`` on their own :sob:!
  * If everything is fine, it'll give a continuation message, just in case you're not ready to send out all the emails
4. ``call_postman`` generates an email for each Secret Santa telling them of their chosen gift recipient.
  * Imports plain text and HTML email templates from the ``templates`` folder
  * Opens a connection to an email server &mdash; currently Gmail
  * Generates a Secret Santa-specific MIME email
  * Embeds a random, PG-13 or safer, festive GIP from [GIPHY](https://giphy.com/)
    * The GIF is temporarily downloaded into the working directory, and deleted after embedding
  * Sends the email to the Secret Santa, and then repeats for all other Secret Santas

### Assumptions and exclusions

## Running the tests

TBC

## License

This repository is licensed under the MIT License - see [LICENSE](LICENSE) file for further details.

## Acknowledgements

* Inspiration from Mark Patton, Stuart Bowe, and Duncan Parkes' [version](https://github.com/deparkes/SecretSanta);
* Lee Munroe's [Responsive HTML Email Template](https://github.com/leemunroe/responsive-html-email-template), which is the basis for the HTML email template used here; and
* Jackie for putting up with my sprints!
