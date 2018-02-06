#!/usr/bin/env python
#coding=utf-8
import time
import csv
import sys
import codecs
from redminelib import Redmine

class redmine_API:
	def __init__(self,url='http://192.168.5.9:8080/redmine', key='83ee8f3d9c1c6c1029a014933e896bace0d4a78a'):
		self.redmine_url = url
		self.redmine_key = key
		self.myredmine = Redmine(self.redmine_url, key=self.redmine_key)
		
	def getProjectIdentifier(self,pname):
		project = self.myredmine.project.all()
		for p in project:
			if str(pname) == str(p.name):
				return p.identifier
		return ''
	
	def getChildProjectIdentifier(self,pname):
		identifier = []
		project = self.myredmine.project.all()
		for p in project:
			try:
				if str(p.parent.name) == pname:
					identifier.append(p.identifier)
			except:
				pass
		return identifier
		
	def getAllProject(self):
		return self.myredmine.project.all()
		
	def getVersion(self, project):
		version = {}
		for i in self.myredmine.version.filter(project_id=project):
			version[i.id] = i.name
		return version
	
	def getUser(self, userid, include='memberships,groups'):
		return self.myredmine.user.get(userid)
		
	def getIssues(self, projectIdentifier, status='Open'):
		start = time.time()
		time1 = time.strftime("%Y-%m-%d", time.localtime())
		time2 = time.strftime("%Y-%m-%d", time.localtime(time.time()- 30*24*60*60))
		information = []
		if status == 'Open':
			issues = self.myredmine.issue.filter(project_id=projectIdentifier,status_id='o')
		elif status == 'Closed':
			issues = self.myredmine.issue.filter(project_id=projectIdentifier, status_id=5, updated_on = "><%s|%s"%(time2,time1))
		count =  len(list(issues))+0.0
		if status == 'Open':
			print 'The total number opened of issues: %s'%count
		elif status == 'Closed':
			print 'The total number closed of issues: %s' % count
		c = 0.0
		for i in issues:
			info = {}
			info['#'] = i.id # #
			info['project'] = i.project # 项目
			info['tracker'] = i.tracker  # 跟踪
			info['status'] = i.status  # 状态
			info['priority'] = i.priority  # 优先级
			info['subject'] = i.subject  # 主题
			info['author'] = i.author  # 作者
			try:
				info['assigned_to'] = i.assigned_to  # 指派给
			except:
				info['assigned_to'] = ''
				print i.id
			info['updated_on'] = i.updated_on  # 更新于
			try:
				info['category'] = i.category  # 类别
			except:
				info['category'] = ''
			info['created_on'] = i.created_on  # 创建于
			info['cf1'] = info['cf2'] = info['cf3'] = info['cf4'] = info['cf5'] = info['cf6'] = info['cf7'] = info['cf8'] =\
			info['cf9'] = info['cf10'] = info['cf11'] = info['cf12'] = info['cf13'] = info['cf14'] = info['cf15'] = ''
			for j in i.custom_fields:
				if j.name == '严重性':info['cf1'] = j.value # 严重性
				elif j.name == '可复现性':info['cf2'] = j.value # 可复现性
				elif j.name == '问题版本':
					if j.value:
						j.value = j.value[0] if type(j.value) == list else j.value
						try:
							project = self.getProjectIdentifier(i.project)
							msg = self.getVersion(project)[int(j.value)]
							info['cf3'] = msg  # 问题版本
						except:
							project = self.getChildProjectIdentifier(i.project)
							for p in project:
								try:
									msg = self.getVersion(p)[int(j.value)]
									info['cf3'] = msg  # 问题版本
									break
								except:
									pass
				elif j.name == '开发工程师':
					if j.value:
						try:
							user = self.getUser(j.value)
							msg = ''.join(list(reversed(str(user).split(' '))))
						except:
							msg = j.value
						info['cf4'] = msg
				elif j.name == '影响分析':info['cf5'] = j.value
				elif j.name == '修正结论':info['cf6'] = j.value
				elif j.name == '问题根因':info['cf7'] = j.value
				elif j.name == '修改方案':info['cf8'] = j.value
				elif j.name == '解决版本':
					if j.value:
						j.value = j.value[0] if type(j.value) == list else j.value
						try:
							project = self.getProjectIdentifier(i.project)
							msg = self.getVersion(project)[int(j.value)]
							info['cf9'] = msg  # 解决版本
						except:
							project = self.getChildProjectIdentifier(i.project)
							for p in project:
								try:
									msg = self.getVersion(p)[int(j.value)]
									info['cf9'] = msg  # 解决版本
									break
								except:
									pass
				elif j.name == '自测结果':info['cf10'] = j.value
				elif j.name == '测试建议':info['cf11'] = j.value
				elif j.name == 'Review工程师':
					if j.value:
						try:
							user = self.getUser(j.value)
							msg = ''.join(list(reversed(str(user).split(' '))))
						except:
							msg = j.value
						info['cf12'] = msg
				elif j.name == 'Review意见':info['cf13'] = j.value
				elif j.name == '测试工程师':
					if j.value:
						try:
							user = self.getUser(j.value)
							msg = ''.join(list(reversed(str(user).split(' '))))
						except:
							msg = j.value
						info['cf14'] = msg
				elif j.name == '验证版本':
					if j.value:
						j.value = j.value[0] if type(j.value) == list else j.value
						try:
							project = self.getProjectIdentifier(i.project)
							msg = self.getVersion(project)[int(j.value)]
							info['cf15'] = msg  # 验证版本
						except:
							project = self.getChildProjectIdentifier(i.project)
							for p in project:
								try:
									msg = self.getVersion(p)[int(j.value)]
									info['cf15'] = msg  # 验证版本
									break
								except:
									pass
			inf = [info['#'],info['project'],info['tracker'],info['status'],info['priority'],info['subject'],info['author'],
			       info['assigned_to'],info['updated_on'],info['category'],info['created_on'],info['cf1'],info['cf2'],info['cf3'],
			       info['cf4'],info['cf5'],info['cf6'],info['cf7'],info['cf8'],info['cf9'],info['cf10'],info['cf11'],info['cf12'],
			       info['cf13'],info['cf14'],info['cf15']]
			information.append(inf)
			c += 1
			rate = c / count
			rate_num = round(rate * 100, 1)
			r = '\rExport progress: %s%%' % rate_num
			sys.stdout.write(r)
			sys.stdout.flush()
		print '\nTime Duration: %s'%(time.time()-start)
		return information
		
class writecsv:
	row0 = ['#','项目','跟踪','状态','优先级','主题','作者','指派给','更新于','类别','创建于',
	        '严重性','可复现性','问题版本','开发工程师','影响分析','修正结论','问题根因','修改方案',
			'解决版本','自测结果','测试建议','Review工程师','Review意见','测试工程师','验证版本']

	def writecsvfile(self, data, filename, newline=''):
		csvfile = open(filename, 'wb')
		csvfile.write(codecs.BOM_UTF8)
		writer = csv.writer(csvfile)
		writer.writerow(self.row0)
		writer.writerows(data)
		csvfile.close()


if __name__ == "__main__":
	# data = redmine_API().getIssues('baistation-v100r001c00','Closed')
	# writecsv().writecsvfile(data, filename='issues-closed.csv')
	data = redmine_API().getIssues('baistation-v100r001c00')
	writecsv().writecsvfile(data, filename='issues-open.csv')
	# print redmine_API().getUser('248')
	# print redmine_API().getProjectIdentifier('BaiBS_RTS')
	# redmine_API().getVersion('baistation-v100r001c00b100-qb')
	# print redmine_API().getAllProject()



			
			