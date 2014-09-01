import re
from itertools import *
from string import *

def identity(x): return x

def draw_markdown_table(headers, *columns):
	print(' | '.join(headers))
	print(' | '.join(map((lambda x: '---'), headers)))
	for row in izip_longest(*columns, fillvalue=' '):
		print(' | '.join(row))

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
	return (vote, comment.author, comment.permalink, vote_time)

def proposal_to_vote(proposal):
	return ('support', proposal.author, proposal.permalink, proposal.created)

def vote_to_voter(vote):
	(author, link) = (vote[1], vote[2])
	return format("/u/%s [^ref](%s)" % (author, link))

def vote_to_time(reltime, vote):
	return format_time_interval(int(vote[3]) - reltime)

def pluralize(n):
	if n == 1:
		return ""
	else:
		return "s"

def format_time_interval(t):
	if t < 60:
		return format("%d second%s" % (t, pluralize(t)))
	elif t < 60 * 60:
		t = t / 60
		return format("%d minute%s" % (t, pluralize(t)))
	elif t < 60 * 60 * 24:
		t = t / (60 * 60)
		return format("%d hour%s" % (t, pluralize(t)))
	else:
		mins, secs = divmod(t, 60)
		hours, mins = divmod(mins, 60)
		days, hours = divmod(hours, 24)
		return format("%d day%s, %02dh%02dm%02ds" % (days, pluralize(days), hours, mins, secs))

def not_duplicate(seen, it):
	r = not it in seen
	seen[it] = True
	return r

def filter_duplicate_votes(votes):
	voted = {}
	return filter((lambda v: not_duplicate(voted, v[1])), votes)

def draw_vote_table(proposal, comments, excluded_authors):

	proposer_vote = proposal_to_vote(proposal)
	reltime = int(proposer_vote[3])

	votes = filter(identity, map(comment_to_vote, comments))
	votes.append(proposer_vote)

	votes = reversed(filter_duplicate_votes(sorted(votes, key=lambda v: -v[3])))
	(supports, opposes) = partition((lambda x: x[0] == 'support'), votes)

	draw_markdown_table(["Support","Time","Oppose","Time"],
		map(vote_to_voter, supports), map(lambda v: vote_to_time(reltime, v), supports),
		map(vote_to_voter, opposes ), map(lambda v: vote_to_time(reltime, v), opposes ))
