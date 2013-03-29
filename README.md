StopForumSpam plugin for web2py
==============

Inspired by Python Weekly Newsletter (thank you phalt/stopspam), I wrote this plugin.

Thanks to stopforumspam.com for the invaluable service provided.

For intranets and/or large forums/boards/communities, making a request to their
API can be tedious... so we load the definitions once and use our db for checks.

Yes, my dear users, I'm looking at you.... Don't abuse their service!

Instructions:
 - go to /appname/plugin_stopforumspam/index
 - download a file from http://www.stopforumspam.com/downloads/ (start small, choose either 1 or 7)
   - needs to be a *_all.zip file
 - upload the downloaded file to the app
 - click on the "Import" button (wait for it.... see the log on the console), until a "ok" pops up in the page

Let's say you uploaded the emails file, now you have a stopforumspam_emails ready to be used.....

Wait for it....
in a Field, you can use

```python
from plugin_stopforumspam import SFS_EMAIL

db.define_table(
    Field('email', requires=[IS_EMAIL(), SFS_EMAIL(db)]),
    Field('comment_body')
)
```

or, in a module of yours
```python
from plugin_stopforumspam import StopForumSpam as SFS

def is_valid_email(email='maybespammer@gmail.com'):
    sfs = SFS(db)
    rec = sfs.check_email(email)
    if not rec:
        return True
    else:
        return False
```
you can pass both to validators and check_* functions 2 common parameters:
- frequency: an integer 
   - *n* means "check only if this object has been spotted at least *n* times"
- since : needs to be a timedelta or something like '1d' for 1 day, '1w' for 1 week, etc.
   - means "check only if this object was last seen timedelta ago" 

Any check_*() function returns a Row instance containing:
- the "something" checked (username, email, ip_address)
- last_seen : last time the "something" was reported, in UTC
- persistent : a boolean meaning you insert that (available later)
- frequency: how many times "something" was reported in the period relative to the file you uploaded

Available objects
- Validators : SFS_USERNAME, SFS_IP, SFS_EMAIL
- functions : .check_username(), .check_ip(), .check_email()


TODO:
- [ ] include db definitions in the module ?
- [ ] more validators ?
- [ ] tests
- [ ] automatic download ? (can be tedious)
- [ ] management interface for pruning old records
- [ ] when importing a new file, previous records must be pruned or added (frequency ?)
- [ ] figure out an algorithm for confidence (0-100)
- [ ] show report progress on the importing phase
- [ ] insert your own records