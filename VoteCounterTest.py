import datetime
import time
import praw
import gzip
import os
import re
from VoteCounterLib import *

submissionLimit = 3 # bot will iterate through this number of submissions
r = praw.Reddit('Proposal Monitor by /u/NLB2')

#r.login("VoteCounterBot", "123qweasd")
proposal_submits = [] #list containing submissions

subreddit = r.get_subreddit('metanarchism')
test_submission = r.get_submission(submission_id = '2eyjul') # test post

for submission in subreddit.get_hot(limit=submissionLimit):
	title = submission.title
	# text = submission.selftext
	
	if "proposal" in title.lower(): # bot is only looking to tally votes in submissions that have 'proposal' in their title
		proposal_submits.append(submission)
		time.sleep(.5)


for x in range(len(proposal_submits)): # iterates through proposal submissions
	voters = [] # this list will store voters.  this prevents voters from voting twice
	supports = [] # store info regarding support votes
	opposes = [] # store info regarding oppose votes
	proposal_submits[x].replace_more_comments(limit=None, threshold=0) #for large threads, this will ensure 
																		#that all comments are searched
	forest_comments = proposal_submits[x].comments #gets forest of 
		#comments with top-level comments as tree roots.  To get
		#replies to comments use comment.replies
	print(proposal_submits[x].title)
	time.sleep(2)
	support_count = 1 #holds the number of supports - assumption is submitter is supporter
	oppose_count = 0 #holds the number of opposes
	voters.append(proposal_submits[x].author)
	prop_create_time = proposal_submits[x].created
	supports.append([proposal_submits[x].author, proposal_submits[x].permalink, 18000]) #Gets to 
	
	print vote_table(proposal_submits[x], forest_comments, [])
