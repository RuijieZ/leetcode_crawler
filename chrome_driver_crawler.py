import requests
import selenium
from requests.auth import HTTPBasicAuth 
from bs4 import BeautifulSoup
import os
import json
import time
import argparse
from collections import deque

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("ProblemID1", help="Problem1 id")
	parser.add_argument("ProblemID2", help="Problem2 id")
	kwargs = parser.parse_args()
	ProblemID1 = int(kwargs.ProblemID1)
	ProblemID2 = int(kwargs.ProblemID2)

	# Read user ids
	fi = open('id.in', 'r')
	id_list = [line.strip() for line in fi.readlines()]
	fi.close()

	dq = deque() 
	for id in id_list:
		dq.append(id)

	# Read exempt list
	whitelist = set()
	
	file = open("whitelist.in", "r") 
	for line in file:
		 info = line.split()
		 if len(info)<3: continue
		 name = info[1]
		 whitelist.add(name)
	file.close()
    
	headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.125 Safari/537.36'} 
	
	# Read all LC problems
	content = requests.get('https://leetcode.com/api/problems/algorithms/').content
	questions = json.loads(content.decode('utf-8'))['stat_status_pairs']

	for question in questions:	
		if question['stat']['frontend_question_id'] == ProblemID1:
			ProblemDsc1 = question['stat']['question__title']
		elif question['stat']['frontend_question_id'] == ProblemID2:
			ProblemDsc2 = question['stat']['question__title']		

	print("Today's checks: ",ProblemDsc1," ",ProblemDsc2)
	
	# Loop over all users
	suspects = []
	

	while len(dq)>0:
		id = dq.popleft()	
		if id=='': continue
		url = 'https://leetcode.com/'+id	
		print(url)
			
		r = requests.get(url,headers = headers) 
		time.sleep(5)
		profile = BeautifulSoup(r.text,features="html.parser") 
	
		recentProblems = profile.select('.list-group-item')[::-1][0:20]
		if len(recentProblems)==0:
			print("		Not Connected, retry later.")			
			dq.append(id)
			continue
			
		flag = 0
	
		for problem in recentProblems:
			items = list(problem.children)
			if len(items)<6: continue			
			name = items[5].text
			status = items[1].text.strip()
			#print(name,status)		
			if name==ProblemDsc1 and status=='Accepted' or name==ProblemDsc2 and status=='Accepted':
				flag = 1
				break
		
		if flag==0 and id in whitelist: 
			print('		suspect but in whitelist:',id)
		elif flag==0:
			print('		suspect:',id)
			suspects.append(id)

	
	print(suspects)
	
if __name__ == "__main__":
    main()	
	
