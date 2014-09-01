from itertools import *
import os
import pickle
import re
import string
import time

NOW = time.time()
MAX_SUBMISSIONS = 50 # submissions to check for proposals
MAX_PROPOSAL_AGE = 14 # days

def identity(x): return x

def markdown_table(*columns, **k):
	header = k['header']
	footers = k['footers']
	result = []
	result.append(' | '.join(header))
	result.append(' | '.join(map((lambda x: '---'), header)))
	for row in izip_longest(*columns, fillvalue=' '):
		result.append(' | '.join(row))
	for footer in footers:
		result.append(' | '.join(footer))
	return "\n".join(result) + "\n"

def extract_vote_value(comment_text):
	match = re.search('^\W*(support|oppose)(?:[.!]|\W*$)', comment_text, re.I|re.M)
	if (match):
		return match.group(1).lower();
	else:
		return None

def partition(pred, iterable):
	trues = []
	falses = []
	for item in iterable:
		if pred(item):
			trues.append(item)
		else:
			falses.append(item)
	return trues, falses

def comment_to_vote(comment):
	vote = extract_vote_value(comment.body)
	if not vote:
		return None
	if comment.edited:
		vote_time = comment.edited
	else:
		vote_time = comment.created
	return (vote, str(comment.author), str(comment.permalink), int(vote_time))

def proposal_to_vote(proposal):
	return ('support', str(proposal.author), str(proposal.permalink), int(proposal.created))

def vote_to_voter(vote):
	(author, link) = (vote[1], vote[2])
	return "/u/%s [^ref](%s)" % (author, link)

def vote_to_time(reltime, vote):
	return format_time_interval(int(vote[3]) - reltime)

def pluralize(n):
	if n == 1:
		return ""
	else:
		return "s"

def format_time_interval(t):
	mins, secs = divmod(t, 60)
	hours, mins = divmod(mins, 60)
	days, hours = divmod(hours, 24)
	if days:
		return "%d day%s, %dh%02dm%02ds" % (days, pluralize(days), hours, mins, secs)
	elif hours:
		return "%d hour%s" % (hours, pluralize(hours))
	elif mins:
		return "%d minute%s" % (mins, pluralize(mins))
	else:
		return "%d second%s" % (secs, pluralize(secs))

def not_duplicate(seen, it):
	r = not it in seen
	seen[it] = True
	return r

def filter_duplicate_votes(votes):
	voted = {}
	return filter((lambda v: not_duplicate(voted, v[1])), votes)

def percent(over, under):
	if over + under:
		return 100.0 * over / (over + under)
	else:
		return None

def tally_vote(proposal, comments):

	proposer_vote = proposal_to_vote(proposal)
	reltime = int(proposer_vote[3])

	votes = filter(identity, map(comment_to_vote, comments))
	votes.append(proposer_vote)

	votes = reversed(filter_duplicate_votes(sorted(votes, key=lambda v: -v[3])))
	(supports, opposes) = partition((lambda x: x[0] == 'support'), votes)

	return (proposal.permalink, proposal.title, supports, opposes, reltime)

def vote_table(supports, opposes, reltime):
	head = ["Support","Time","Oppose","Time"]
	foot = [["**Totals**",""], ["%d" % len(supports), "", "%d" % len(opposes), ""]]

	p = percent(len(supports), len(opposes))
	if p is not None:
		foot.append(["**%.2f%% support**" % p, ""])

	return markdown_table(
		map(vote_to_voter, supports), map(lambda v: vote_to_time(reltime, v), supports),
		map(vote_to_voter, opposes ), map(lambda v: vote_to_time(reltime, v), opposes ),
		header=head, footers=foot)

def cached(callback, filename, seconds):
	if os.path.isfile(filename) and time.time() < os.path.getmtime(filename) + seconds:
		with open(filename) as f:
			return pickle.load(f)
	result = callback()
	tempfile = filename + ".new"
	with open(tempfile, 'wb') as f:
		pickle.dump(result, f)
	os.rename(tempfile, filename)
	return result

def readlines(filename): return [line.strip() for line in open(filename)]

def is_proposal(submission):
	return "proposal" in submission.title.lower()

def markdown_link(text, url):
	text = text.replace("]", "\\]") # TODO: do this correctly
	return "[%s](%s)" % (text, url)

def markdown_tally(tally):
	(permalink, title, supports, opposes, reltime) = tally

	markdown_title = markdown_link(title, permalink)
	sections = [markdown_title]
	voters = len(supports) + len(opposes)

	if voters: # with the current tally method, this will always be true
		sections.append(vote_table(supports, opposes, reltime))
	else:
		sections.append("(No votes yet.)")
	return "\n\n---\n\n".join(sections)

def too_old_to_tally(submission):
	t = submission.created
	return NOW - t > MAX_PROPOSAL_AGE * 24 * 60 * 60

def submit_or_update_submission(r, username, subreddit_name, title, body):
	subreddit = r.get_subreddit(subreddit_name)
	for submission in subreddit.get_new(limit=MAX_SUBMISSIONS):
		if str(submission.author) == username and str(submission.title) == title:
			submission.edit(body)
			return
	r.submit(subreddit, title, text=body)

def collect_tallies(r, subreddit_name):
	subreddit = r.get_subreddit(subreddit_name)
	print "Collecting tallies..."
	tallies = []
	for submission in subreddit.get_new(limit=MAX_SUBMISSIONS):
		if not is_proposal(submission):
			continue
		if too_old_to_tally(submission):
			break
		submission.replace_more_comments(limit=None, threshold=0)
		forest_comments = submission.comments
		tallies.append(tally_vote(submission, forest_comments))
	return tallies
