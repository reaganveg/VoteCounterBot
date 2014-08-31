import datetime
import time
import praw
import gzip
import os
import re

submissionLimit = 1 # bot will iterate through this number of submissions
r = praw.Reddit('Proposal Monitor by /u/NLB2')

r.login("VoteCounterBot", "123qweasd")
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
	
	for com in forest_comments:
		top_lvl_comment = com.body.lower() #com.body is the text body of the comment
		poster = com.author
		if poster == "NLB2FirstBot":
			continue
		re_comment = re.search('^\W*(support|oppose)(?:[.!]|\W*$)', top_lvl_comment, re.I|re.M)
		if com.edited:
			com_time = com.edited - prop_create_time
		else:
			com_time = com.created - prop_create_time
		if re_comment:
			if poster in voters: #ignore post if the comment poster already voted
				continue
			elif "support" == re_comment.group(0).lower(): #in top_lvl_comment and "might support" not in top_lvl_comment and "oppose" not in top_lvl_comment:
				print("/u/", poster, com.body)
				support_count += 1
				voters.append(poster)
				supports.append([poster, com.permalink, com_time])
			elif "oppose" == re_comment.group(0).lower(): #in top_lvl_comment and "support" not in top_lvl_comment:
				print("/u/", poster, com.body)
				oppose_count += 1
				voters.append(poster)
				opposes.append([poster, com.permalink, com_time])
		
	cur_time = time.ctime()
	print("Vote Count as of", cur_time, "Eastern")
	print("Support:", support_count)
	print("Oppose:", oppose_count)
	print("Voters:", voters)
	cur_time_str = "Vote Count as of " + str(cur_time) + " Eastern"
	about_str = "VoteCounterBot created by /u/NLB2"
	usage_str = "\n\nVoteCounterBot counts votes in top-level comments only.\n" + \
	"For your vote to count, please type 'support' or 'oppose' on its own line like this:\n\n" + \
	"    Support\n\nYou may have as much text in your comment as you'd like, but VoteCounterBot will\n" + \
	"only register your vote if it is on its own line.\nVoteCounterBot automatically counts the proposer\n" + \
	"as a supporter.  VoteCounterBot is case insensitive."
	
	table_str = "Support | Time | Oppose | Time \n"
	table_str += "--- | --- | --- | ---\n"
	
	x = 0
	while x < len(supports) or x < len(opposes):
		if x < len(supports) and x < len(opposes):
			support_tm = time.strptime(time.ctime(supports[x][2]), "%a %b %d %H:%M:%S %Y")
			support_tm_str = time.strftime("%dD+%H:%M", support_tm)
			oppose_tm = time.strptime(time.ctime(opposes[x][2]), "%a %b %d %H:%M:%S %Y")
			oppose_tm_str = time.strftime("%dD+%H:%M", oppose_tm)
			table_str += "/u/"+str(supports[x][0]) + "[^ref](" + str(supports[x][1]) + ")" + \
			" | " + support_tm_str + \
			" | " + "/u/"+str(opposes[x][0]) + "[^ref](" + str(opposes[x][1]) + ") " + \
			+ "| " + oppose_tm_str + "\n"
		elif x < len(supports):
			support_tm = time.strptime(time.ctime(supports[x][2]), "%a %b %d %H:%M:%S %Y")
			support_tm_str = time.strftime("%dD+%H:%M", support_tm)
			table_str += "/u/"+ str(supports[x][0]) + "[^ref](" + str(supports[x][1]) + ") " + \
			" | " + support_tm_str + " | \n"
		elif x < len(opposes):
			oppose_tm = time.strptime(time.ctime(opposes[x][2]), "%a %b %d %H:%M:%S %Y")
			oppose_tm_str = time.strftime("%dD+%H:%M", oppose_tm)
			table_str += " | (/u/" + str(opposes[x][0]) + str(opposes[x][1]) + ")[^ref] | " + \
			oppose_tm_str + "\n"
		x += 1
	
	table_str += "**Totals** | | | \n" + str(support_count) + " | | " + str(oppose_count) + " | "
	total_str = cur_time_str + "\n\n" + table_str + "\n\n" + about_str + usage_str
	time.sleep(2)
	#test_submission.add_comment(total_str)
	print(total_str)
	
	with gzip.open("output.txt.gz", 'wb') as f_out:
		f_out.write(bytes(total_str, 'UTF-8'))
	
	
	
