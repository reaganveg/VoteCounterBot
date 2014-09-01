import datetime
import time
import praw
import gzip
import os
import re
import sys
from string import split

from VoteCounterLib import *

(username, password) = readlines('login.txt')
poll_subreddits = map(split, readlines('poll-subreddits.txt'))

r = praw.Reddit('Proposal Monitor by /u/NLB2')
r.login(username, password)

for in_out in poll_subreddits:
	subreddit_name = in_out[0]
	cache_file = "tallies-for-%s.dat" % subreddit_name
	print "Handling votes in /r/%s" % subreddit_name
	tallies = cached(lambda: collect_tallies(r, subreddit_name), cache_file, 60*60*2)

	title = "Recent proposals and vote tallies in /r/%s." % subreddit_name
	headers = [title]
	footers = ["To be counted by this bot, votes must consist of 'support' or 'oppose' at the start of a line in its own sentence.\n\nVotes must be top-level replies.\n\nProposals must contain the word 'proposal'."]

	combined_summary = "\n\n---\n\n---\n\n".join(headers + map(markdown_tally, tallies) + footers)

	for output_subreddit_name in in_out[1:]:
		submit_or_update_submission(r, username, output_subreddit_name, title, combined_summary)
		print "submitted tallies for /r/%s to /r/%s" % (subreddit_name, output_subreddit_name)

