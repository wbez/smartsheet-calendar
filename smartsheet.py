import smartsheetclient,json
from collections import OrderedDict
from datetime import datetime, date, timedelta
import os
import pandas as pd
# BDay is business day, not birthday...
from pandas.tseries.offsets import BDay

def make_context():
	today = date.today().strftime('%Y-%m-%d')
	two_days_ago = date.today()-timedelta(days=1)
	two_days_later = date.today()+timedelta(days=1)
	two_weeks_later = date.today()+timedelta(days=10)
	yesterday = date.today()-timedelta(days=1)
	tomorrow = date.today()+timedelta(days=1)
	showboards_today = pd.datetime.today()
	showboards_two_days = showboards_today - BDay(3)
	showboards_two_weeks = showboards_today + BDay(7)

	token = os.environ['SMARTSHEET_TOKEN']

	client = smartsheetclient.SmartsheetClient(token)
	client.connect()
	sheet_list = client.fetchSheetList()

	showboardsid = '2812472127186820'
	rundownsid = '3208506766583684'
	pegsid = '3311994003580804'
	featuresid = '5468187845257092'

	showboards = client.fetchSheetById(showboardsid)
	rundowns = client.fetchSheetById(rundownsid)
	pegs = client.fetchSheetById(pegsid)
	features = client.fetchSheetById(featuresid)

	showboards_context = {}
	showboards_context['DAYS'] = OrderedDict()

	assignment_context = {}
	assignment_context['DAYS'] = OrderedDict()

	planning_context = {}
	planning_context['DAYS'] = OrderedDict()
	planning_context['FEATURES'] = []

	columns = [col.title for col in showboards.columns]
	print "running report for %s" % today

	print "processing showboards"
	for row in showboards.rows:
		
		show = row[0]
		day = row[3]
		if day != None and show != None:
			
			day_obj = pd.datetime.strptime(day,'%Y-%m-%d')
			day_of_week = day_obj.strftime('%A')
			date_str = day_obj.strftime('%b %d').lstrip("0").replace(" 0", " ")
			today_flag = (day_obj.strftime('%Y-%m-%d')==today)

			if day_obj >= showboards_two_days and day_obj <= showboards_two_weeks:
				
				if day not in showboards_context['DAYS']: 
					showboards_context['DAYS'][day] = {'day_of_week': day_of_week, 'date_str':date_str, 'shows':OrderedDict(),'today':today_flag}
				if show not in showboards_context['DAYS'][day]['shows']: 
					showboards_context['DAYS'][day]['shows'].update({show:[]})
			
				day_context = {}
				day_context['show'] = show
				day_context['status'] = row[1]
				day_context['segment'] = row[2]
				day_context['story_slug'] = row[4]
				day_context['segment_type'] = row[5]
				day_context['reporter'] = row[6]
				if row[6] != None:
					day_context['initials'] = initials(row[6])
				day_context['category'] = row[7]

				showboards_context['DAYS'][day]['shows'][show].append(day_context)

	print "processing rundowns"
	for row in rundowns.rows:
		
		if row[3]=='SAMPLE DAY':
			break
		cast = row[1]
		day = row[2]
		on_board = row[8]
		item_type = row[7]
		if day != None and cast != None and item_type != 'Promo':
			day_obj = datetime.strptime(day,'%Y-%m-%d').date()
			day_of_week = day_obj.strftime('%A')
			date_str = day_obj.strftime('%b %d').lstrip("0").replace(" 0", " ")
			today_flag = (day_obj.strftime('%Y-%m-%d')==today)

			day_context = {}
			day_context['cast'] = cast
			day_context['status'] = row[0]
			day_context['story_slug'] = row[3]
			day_context['length'] = row[4]
			day_context['reporter'] = row[5]
			if row[5] != None:
				day_context['initials'] = initials(row[5])
			day_context['editor'] = row[6]
			day_context['type'] = row[7]
			day_context['category'] = row[11]
			day_context['on_board'] = row[8]

			if day_obj >= two_days_ago and day_obj <= two_days_later:
				
				if day not in planning_context['DAYS']: 
					planning_context['DAYS'][day] = {'day_of_week': day_of_week, 'date_str':date_str, 'today':today_flag, 'cast_items':[], 'anchors':[], 'features': []}

				if row[7] == 'Feature':
					if not any(d['story_slug'] == row[3] for d in planning_context['DAYS'][day]['features']):
						planning_context['DAYS'][day]['features'].append(day_context)
				elif row[7] == 'Anchor':
					planning_context['DAYS'][day]['anchors'].append(day_context)
				elif not any(d['story_slug'] == row[3] for d in planning_context['DAYS'][day]['cast_items']):
					planning_context['DAYS'][day]['cast_items'].append(day_context)

	# for row in pegs.rows:
	# 	cast = row[1]
	# 	reporter = row[5]
	# 	day = row[2]
	# 	if day != None and reporter != None:
	# 		day_obj = datetime.strptime(day,'%Y-%m-%d').date()
	# 		day_of_week = day_obj.strftime('%A')
	# 		date_str = day_obj.strftime('%b %d').lstrip("0").replace(" 0", " ")

	# 		if day_obj >= two_days_ago and day_obj <= two_days_later:
				
	# 			if day not in planning_context['DAYS']: 
	# 				planning_context['DAYS'][day] = {'day_of_week': day_of_week, 'date_str':date_str, 'casts':OrderedDict()}
	# 			if cast not in planning_context['DAYS'][day]['casts']: 
	# 				planning_context['DAYS'][day]['casts'].update({cast:[]})
			
	# 			context = {}
	# 			context['cast'] = cast
	# 			context['status'] = row[0]
	# 			context['story_slug'] = row[3]
	# 			context['length'] = row[4]
	# 			context['reporter'] = reporter
	# 			if reporter != None:
	# 				context['initials'] = initials(reporter)
	# 			context['editor'] = row[6]
	# 			context['type'] = row[7]
	# 			context['category'] = row[10]

	# 			if row[7] == 'Feature':
	# 				planning_context['DAYS'][day]['casts']['Features'].append(day_context)
	# 			else:
	# 				planning_context['DAYS'][day]['casts'][cast].append(context)
	print "processing features"
	for row in features.rows:
		
		cast = row[1]
		reporter = row[5]
		audio_type = row[7]
		day = row[2]

		if audio_type == 'Feature' and reporter != None and day != None:

			day_obj = datetime.strptime(day,'%Y-%m-%d').date()
			day_of_week = day_obj.strftime('%A')
			date_str = day_obj.strftime('%b %d').lstrip("0").replace(" 0", " ")

			if day_obj > tomorrow:
				context = {}
				context['day'] = day_obj
				context['date']= date_str
				context['status'] = row[0]
				context['cast'] = row[1]
				context['story_slug'] = row[3]
				context['format'] = row[4]
				context['reporter'] = reporter
				if reporter != None:
					context['initials'] = initials(reporter)
				context['editor'] = row[6]
				context['type'] = row[7]
				context['category'] = row[10]

				planning_context['FEATURES'].append(context)


	showboards_context['DAYS'] = OrderedDict(sorted(showboards_context['DAYS'].iteritems(), key=lambda x: x[0]))
	assignment_context['DAYS'] = OrderedDict(sorted(assignment_context['DAYS'].iteritems(), key=lambda x: x[0]))
	planning_context['DAYS'] = OrderedDict(sorted(planning_context['DAYS'].iteritems(), key=lambda x: x[0]))
	planning_context['FEATURES'] = sorted(planning_context['FEATURES'], key=lambda k: k['day'])

	remove_days(planning_context['FEATURES'])

	context = {'showboards':showboards_context, 'assignments': assignment_context, 'planning': planning_context}
	with open('/srv/smartsheet/static/smartsheet.json', 'w') as outfile:
		print "outputting json"
		json.dump(context, outfile, sort_keys=True)

def initials(name):
	output = "".join(item[0].upper() for item in name.split())
	return output

def remove_days(entries):
	for item in entries:
		del item['day']

if __name__ == '__main__':
	make_context()