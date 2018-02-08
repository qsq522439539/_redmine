#!/usr/bin/env python
#coding=utf-8
import os
import sys
import re
import getopt
import urllib
import urllib2
import tempfile
import shutil
import http.cookiejar
from redminelib import Redmine

def usage():
	print 'Usage: -P [projectname] -u [username] -p [password] -h'
	print '\t-P option: project name'
	print '\t-u option: username'
	print '\t-p option: password'
	print '\t-h option: print this help information'
	sys.exit(10)

def argumentcheck():
	configs = {}
	if len(sys.argv) < 1:
		usage()
	opts, args = getopt.getopt(sys.argv[1:], "hP:u:p:")
	for op, value in opts:
		if op == "-P":
			configs['projectname'] = value
		elif op == "-u":
			configs['username'] = value
		elif op == "-p":
			configs['password'] = value
		elif op == "-h":
			usage()
	if len(configs.keys()) != 3:
		if not 'projectname' in configs.keys():
			print 'please enter the project name...'
		if not 'username' in configs.keys():
			print 'please enter the username...'
		if not 'password' in configs.keys():
			print 'please enter the password...'
		sys.exit(10)
	return configs

class redmine_:
	
	def __init__(self,url='http://192.168.5.9:8080/redmine', key='83ee8f3d9c1c6c1029a014933e896bace0d4a78a'):
		self.redmine_url = url
		self.redmine_key = key
		self.myredmine = Redmine(self.redmine_url, key=self.redmine_key)
	
	def getProjectIdentifier(self, projectName):
		identifier = ''
		project = self.myredmine.project.all()
		for p in project:
			if str(projectName) == str(p.name):
				identifier = p.identifier
		if identifier != '':
			return identifier
		else:
			print 'please check the project name...'
			sys.exit(10)
		
	def downloadCsv(self, projectName, username, password):
		identifier = self.getProjectIdentifier(projectName)
		login_url = 'http://192.168.5.9:8080/redmine/login?back_url=http%3A%2F%2F192.168.5.9%3A8080%2Fredmine%2F'
		Login_url = 'http://192.168.5.9:8080/redmine/login'
		csv_url = 'http://192.168.5.9:8080/redmine/projects/'+str(identifier)+'/issues.csv?utf8=%E2%9C%93&set_filter=1&f%5B%5D=status_id' \
		          '&op%5Bstatus_id%5D=o&v%5Bstatus_id%5D%5B%5D=&f%5B%5D=tracker_id&op%5Btracker_id%5D=%3D&v%5Btracker_id' \
		          '%5D%5B%5D=2&v%5Btracker_id%5D%5B%5D=1&group_by=status&sort=tracker%2Cstatus%2Cupdated_on&csv%5Bcolumns%5D=all'
		csv_url2 = 'http://192.168.5.9:8080/redmine/projects/'+str(identifier)+'/issues.csv?utf8=%E2%9C%93&set_filter=1&f%5B%5D=status_id' \
		           '&op%5Bstatus_id%5D=c&v%5Bstatus_id%5D%5B%5D=&f%5B%5D=tracker_id&op%5Btracker_id%5D=%3D&v%5Btracker_id' \
		           '%5D%5B%5D=2&v%5Btracker_id%5D%5B%5D=1&f%5B%5D=updated_on&op%5Bupdated_on%5D=%3E%3Ct-&v%5Bupdated_on' \
		           '%5D%5B%5D=30&group_by=status&sort=updated_on&csv%5Bcolumns%5D=all'
		user_agent = r'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.75 Safari/537.36'
		headers = {'User-Agent': user_agent, 'Connection': 'keep-alive'}
		t = tempfile.mkdtemp()
		cookiefile = t+ '\cookie.txt'
		cookie_aff = http.cookiejar.MozillaCookieJar(cookiefile)
		
		handler = urllib2.HTTPCookieProcessor(cookie_aff)
		opener = urllib2.build_opener(handler)
		# 打开界面
		login_request = urllib2.Request(login_url, headers=headers)
		try:
			login_response = opener.open(login_request)
		except urllib2.HTTPError, e:
			print 'login_error:', e.getcode()
			print e.geturl()
			print "-------------------------"
			print e.info()
			print e.read()
		print login_response.read()
		cookie_aff.save(ignore_discard=True, ignore_expires=True)
		data = login_response.read()
		authenticity_token = re.findall('name="authenticity_token" value="(.*?)" />', data)[0]
		values = {'utf8': '✓',
		          'authenticity_token': '%s' % authenticity_token,
		          'back_url': 'http://192.168.5.9:8080/redmine/', 'username': '%s'%username, 'password': '%s'%password,
		          'login': '登录 »'}
		postdata = urllib.urlencode(values).encode()
		# 登录
		cookie_aff.load(cookiefile, ignore_discard=True, ignore_expires=True)
		Login_request = urllib2.Request(Login_url, postdata, headers=headers)
		try:
			Login_response = opener.open(Login_request)
		except urllib2.HTTPError, e:
			print 'Login_error:', e.getcode()
			print e.geturl()
			print "-------------------------"
			print e.info()
			print e.read()
		cookie_aff.save(ignore_discard=True, ignore_expires=True)
		if 'flash_error' in Login_response.read():
			print 'invalid username or password...'
			sys.exit(10)
		# 下载Open问题单
		cookie_aff.load(cookiefile, ignore_discard=True, ignore_expires=True)
		csv_request = urllib2.Request(csv_url, headers=headers)
		try:
			csv_response = opener.open(csv_request)
		except urllib2.HTTPError, e:
			print e.getcode()
			print e.geturl()
			print "-------------------------"
			print e.info()
			print e.read()
		data = csv_response.read()
		with open("issues.csv", "wb") as code:
			code.write(data)
	
		# 下载closed问题单
		cookie_aff.load(cookiefile, ignore_discard=True, ignore_expires=True)
		csv_request2 = urllib2.Request(csv_url2, headers=headers)
		try:
			csv_response2 = opener.open(csv_request2)
		except urllib2.HTTPError, e:
			print e.getcode()
			print e.geturl()
			print "-------------------------"
			print e.info()
			print e.read()
		data = csv_response2.read()
		with open("issues(1).csv", "wb") as code:
			code.write(data)
		shutil.rmtree(t)
			
if __name__ == "__main__":
	configs = argumentcheck()
	redmine_().downloadCsv(configs['projectname'], configs['username'], configs['password'])
	# redmine_().downloadCsv('BaiBS_RTS','qinshiqiang','12345678')




		