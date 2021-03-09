# Zulip forum bot

Someone was trying to use Zulip as a Q&A forum.  Threaded topics make
this possible, but there is still a problem with keeping things
organized.  Inspired by their workaround, this code will:

* When an emoji reaction (such as :check_mark:) is given, it will
  rename the topic of that thread to include the emoji.  Thus, it is
  easy to mark topics as resolved, in progress, etc.

* If your audience doesn't understand threads and comments in existing
  threads, that's annoying.  You can always rename, or you con comment
  with the :scissors: emoji and it will cut it for you.  You still
  need to rename the topic yourself, but this seems to be less
  annoying mouse strokes.


## Installation and invocation

This is currently alpha-quality but it works for its purpose.  If this
is useful comment and it can be improved.

Currently no installation, clone the repository and run
`zulip-forum-bot.py {zuliprc-file}`.  The first argument is the
zuliprc file you can get from the Zulip server.


## Configuration

Currently no configuration, open and edit the file and edit various
variables to your needs:

* `ALLOW_STREAMS`: it will only operate on messages in these
streams.
* `ALLOW_USERS`: it will only operate when these users make the reaction.
* `ALLOW_EMOJIS`: it will only operate on these reaction emojis.


## Development status and maintenance

This is proof of concept but works.  If you find it useful, get in
touch and we can improve it some.
