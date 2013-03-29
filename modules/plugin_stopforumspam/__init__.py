# -*- coding: utf-8 -*-

import zipfile
import os
import csv
import datetime
from gluon.validators import Validator, translate

def transform_duration(duration):
    if isinstance(duration, datetime.timedelta):
        return duration
    elif isinstance(duration, str):
        allowed_identifiers = ('h', 'd', 'w', 'm', 'y')
        number, identifier = duration[:-1], duration[-1]
        if identifier not in allowed_identifiers:
            raise Exception, "not a valid identifier %s" % identifier
        try:
            int(number)
        except:
            raise Exception, "not a valid integer %s" % number
        if identifier == 'h':
            return datetime.timedelta(hours=int(number))
        elif identifier == 'd':
            return datetime.timedelta(days=int(number))
        elif identifier == 'w':
            return datetime.timedelta(days=7*int(number))
        elif identifier == 'm':
            return datetime.timedelta(days=30*int(number))
        elif identifier == 'y':
            return datetime.timedelta(days=365*int(number))
    else:
        raise Exception, "only str or timedelta allowed"


class StopForumSpam(object):
    def __init__(self, db):
        self.db = db

    def import_from_file(self, filename):
        allowed = (
            'listed_username_%s_all.zip',
            'listed_email_%s_all.zip',
            'listed_ip_%s_all.zip'
            )
        durations = (1, 7, 30, 90, 180, 365)
        all_of_them = [a % b for b in durations for a in allowed]
        if os.path.basename(filename) not in all_of_them:
            raise Exception, "File not recognized"
        if not os.path.isfile(filename):
            raise Exception, "Can't locate file %s" % filename
        contentname = os.path.basename(filename).replace('.zip', '.txt')
        archive = zipfile.ZipFile(filename)
        with archive.open(contentname, 'r') as content:
            if 'listed_username_' in filename:
                self.import_usernames(content)
            elif 'listed_email_' in filename:
                self.import_emails(content)
            elif 'listed_ip_' in filename:
                self.import_ips(content)

    def import_usernames(self, content):
        final = self.db.stopforumspam_usernames
        spamreader = csv.reader(content, escapechar="\\")
        x = 0
        for row in spamreader:
            x += 1
            final.update_or_insert(final.username == row[0],
                username=row[0],
                frequency=row[1],
                last_seen=row[2]
                )
            if x % 1000 == 0:
                self.db.commit()
        self.db.commit()
        return x

    def import_emails(self, content):
        final = self.db.stopforumspam_emails
        spamreader = csv.reader(content, escapechar="\\")
        x = 0
        for row in spamreader:
            x += 1
            final.update_or_insert(final.email == row[0],
                email=row[0],
                frequency=row[1],
                last_seen=row[2]
                )
            if x % 1000 == 0:
                self.db.commit()
        self.db.commit()
        return x

    def import_ips(self, content):
        final = self.db.stopforumspam_ips
        spamreader = csv.reader(content, escapechar="\\")
        x = 0
        for row in spamreader:
            x += 1
            final.update_or_insert(final.ip_address == row[0],
                ip_address=row[0],
                frequency=row[1],
                last_seen=row[2]
                )
            if x % 1000 == 0:
                self.db.commit()
        self.db.commit()
        return x


    def check_ip(self, ip, frequency=50, since=datetime.timedelta(days=7)):
        timelimit = datetime.datetime.utcnow() - transform_duration(since)
        t = self.db.stopforumspam_ips
        rec = self.db(
            (t.ip_address == ip) &
            (t.frequency >= frequency) &
            (t.last_seen >= timelimit)
            ).select().first()
        return rec

    def check_username(self, username, frequency=50, since=datetime.timedelta(days=7)):
        timelimit = datetime.datetime.utcnow() - transform_duration(since)
        t = self.db.stopforumspam_usernames
        rec = self.db(
            (t.username == username) &
            (t.frequency >= frequency) &
            (t.last_seen >= timelimit)
            ).select().first()
        return rec

    def check_email(self, email, frequency=50, since=datetime.timedelta(days=7)):
        timelimit = datetime.datetime.utcnow() - transform_duration(since)
        t = self.db.stopforumspam_emails
        rec = self.db(
            (t.username == email) &
            (t.frequency >= frequency) &
            (t.last_seen >= timelimit)
            ).select().first()
        return rec

class SFS_IP(Validator):

    def __init__(self, 
        db, 
        frequency=50, 
        since=datetime.timedelta(days=7), 
        error_message='Suspicious IP'
        ):
        self.frequency = frequency
        self.since = since
        self.error_message = error_message
        self.db = db

    def __call__(self, value):
        t = self.db.stopforumspam_ips
        timelimit = datetime.datetime.utcnow() - transform_duration(self.since)
        rec = self.db(
            (t.ip_address == value) &
            (t.frequency >= self.frequency) &
            (t.last_seen >= timelimit)
            ).select().first()
        if not rec:
            return (value, None)
        else:
            return (value, translate(self.error_message))

class SFS_EMAIL(Validator):

    def __init__(self, 
        db, 
        frequency=50, 
        since=datetime.timedelta(days=7), 
        error_message='Suspicious email address'
        ):
        self.frequency = frequency
        self.since = since
        self.error_message = error_message
        self.db = db

    def __call__(self, value):
        t = self.db.stopforumspam_emails
        timelimit = datetime.datetime.utcnow() - transform_duration(self.since)
        rec = self.db(
            (t.email == value) &
            (t.frequency >= self.frequency) &
            (t.last_seen >= timelimit)
            ).select().first()
        if not rec:
            return (value, None)
        else:
            return (value, translate(self.error_message))

class SFS_USERNAME(Validator):

    def __init__(self, 
        db, 
        frequency=50, 
        since=datetime.timedelta(days=7), 
        error_message='Suspicious Username'
        ):
        self.frequency = frequency
        self.since = since
        self.error_message = error_message
        self.db = db

    def __call__(self, value):
        t = self.db.stopforumspam_usernames
        timelimit = datetime.datetime.utcnow() - transform_duration(self.since)
        rec = self.db(
            (t.username == value) &
            (t.frequency >= self.frequency) &
            (t.last_seen >= timelimit)
            ).select().first()
        if not rec:
            return (value, None)
        else:
            return (value, translate(self.error_message))

