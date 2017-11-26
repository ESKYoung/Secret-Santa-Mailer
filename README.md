# Secret Santa Mailer

Double-blind random selection to pair a list of Secret Santas with each other. Each Secret Santa is emailed their randomly-selected gift recipient directly.

## Getting started

### Prerequisites

You need the following to run this code:

1. Python 3;
2. The ``pandas`` module;
3. Local clone of this repository;
4. ``.csv`` file with Secret Santas' names and emails;
    * Add a header row - any will do!
    * Add data from Row 2 onwards
    * First column should be names, second column should be email addresses
    * Use the repository's [template](templates/Secret_Santa_Template.csv) if you'd like!
5. Access to a suitably festive mailbox; and
6. A GIPHY API token &mdash; get one [here](https://developers.giphy.com)!

To ensure everything runs smoothly, remember the code:

* Requires a minimum of two names, and they should all be **unique**;
* Accepts only valid email addresses, but there can be duplicates; and
* Is currently setup for Gmail accounts only;.

### Running the code

Navigate to your local repository using command line, then run this code:

~~~
python secret_santa_mailer.py <<<EMAIL ADDRESS>> <<<CSV FILENAME>>> <<<KEEP GIFS VALUE>>>
~~~

where ``<<<EMAIL ADDRESS>>>`` is a valid mailbox from where emails are sent to each Secret Santa, and ``<<<CSV FILENAME>>>`` is the ``.csv`` file from Step 4, including the full path if it's not in your working directory. **Both parameters are required**.

``<<<KEEP GIFS VALUE>>>`` is *optional*; if this value is set to ``1``, ``GIF``s in the emails are saved, otherwise they're deleted as soon as they been embedded.

## How it works

Here's how the code works:

1. Checks that the outgoing email address is valid;
2. Loads the ``.csv`` file containing Secret Santa details;
3. Splits out names, and email addresses from Step 2;
4. Requests outgoing email address password, and GIPHY API token; and
5. Executes the ``secret_santa_mailer`` function.

This ``secret_santa_mailer`` function works as follows:

1. ``find_sleighs`` checks enough names, and email addresses were supplied;
2. ``check_reindeers`` ensures email addresses are valid;  
3. ``secret_santa_pairings`` randomly pairs Secret Santas with each other; and
4. ``call_postman`` generates an email for each Secret Santa telling them of their chosen gift recipient, with an embedded festive ``GIF``.
    * ``mime_giphy`` temporarily downloads a random, PG-13 or safer, festive ``GIF``, and generates a MIME image.

## Running the tests

To run the unit tests, navigate to your local repository using command line, then run this code:

~~~
python -m unittest tests_secret_santa_mailer
~~~

## License

This repository is licensed under the MIT License - see [LICENSE](LICENSE) file for further details.

## Acknowledgements

* Inspiration from Mark Patton, Stuart Bowe, and Duncan Parkes' [version](https://github.com/deparkes/SecretSanta);
* Lee Munroe's [Responsive HTML Email Template](https://github.com/leemunroe/responsive-html-email-template), which is the basis for the HTML email template used here; and
* Jackie for putting up with my sprints!
