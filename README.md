Batchmate
============

Using Batchmate you can retrieve homework assignments from different sources, with fresh folder structures.

Fetchmail
----------

Currently the only supported source is an email account, and mostly a Gmail account.

### Usage

Using the Fetchmail utility is easy. You should just the run the following command:

    python fetchmail.py BASE_PATH --user USER --pass PASS --search GMAIL_SEARCH_CRITERIA --subject REGEX --body REGEX

A full list of options is available by running `python fetchmail.py`.  
Alternatively, you may set the options in the source file.

### Examples

To get emails that have attachments and are labeled as `hw1`:

    python fetchmail.py ~/hws  --search "has:attachment label:hw1"

To format the directory structures using an 8-digit student ID which could be present anywhere in the subject or body:

    python fetchmail.py ~/hws  --subject "([0-9]{8})" --body "([0-9]{8})"

Using this command if an email with the subject `hw2-87102262` was retrieved, the corresponding folder created for this homework submission would be just `87102262`. If no such pattern is found, a workaround for setting unique folder names is used.

To ignore some specific extension like `.exe` or `.iso` you may use the command like this:

    python fetchmail.py ~/hws --ignore-exts exe iso

You can resume your retrieving process using the `--start` command. You can stop the script and save the last number of downloaded email and then later use this option to resume:

    python fetchmail.py ~/hws --start 120

Please note that this option assumes that the mail server's response to the search request stays the same. If some new mails arrived, or for any reason the mail server responds with different sets of emails, this numbering would not be valid.

Future
----------
In the near future the following features would be added to Batchmate:

* Support for filtering results based on more options
* Fetching results from other sources like an authentication-required page of submissions, a FTP server and etc.

