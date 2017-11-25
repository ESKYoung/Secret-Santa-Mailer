# Secret Santa Mailer

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

where ``<<<EMAIL ADDRESS>>>`` is a valid mailbox from where emails are sent to each Secret Santa, and ``<<<CSV FILENAME>>>`` is the ``.csv`` file from Step 4, including the full path if it's not in your local repo.

## How it works

### Assumptions

## Running the tests

TBC

## License

This repository is licensed under the MIT License - see [LICENSE.md](LICENSE.md) file for details.

## Acknowledgements

* Inspiration from Mark Patton, Stuart Bowe, and Duncan Parkes' [version](https://github.com/deparkes/SecretSanta);
* Lee Munroe's [Responsive HTML Email Template](https://github.com/leemunroe/responsive-html-email-template), which is the basis for the HTML email template used here; and
* Jackie for putting up with my sprints!
