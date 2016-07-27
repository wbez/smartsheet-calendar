import smartsheet
from collections import OrderedDict
from datetime import datetime, date, timedelta
import os, json
import pandas as pd
# BDay is business day, not birthday...
from pandas.tseries.offsets import BDay

FILE_DIR = os.path.dirname(os.path.realpath(__file__))

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

	client = smartsheet.Smartsheet(token)

	showboardsid = '2812472127186820'
	rundownsid = '3208506766583684'
	pegsid = '3311994003580804'
	featuresid = '5468187845257092'

	showboards = client.Sheets.get_sheet(showboardsid,page_size=100000)
	rundowns = client.Sheets.get_sheet(rundownsid,page_size=100000)
	# pegs = client.Sheets.get_sheet(pegsid,page_size=100000)
	features = client.Sheets.get_sheet(featuresid,page_size=100000)

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
		
		show = row.cells[0].value
		day = row.cells[3].value

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
				day_context['status'] = row.cells[1].value
				day_context['segment'] = row.cells[2].value
				day_context['story_slug'] = row.cells[4].value
				day_context['segment_type'] = row.cells[5].value
				day_context['reporter'] = row.cells[6].value
				if row.cells[6].display_value != None:
					day_context['initials'] = initials(row.cells[6].display_value)
				elif row.cells[6].value != None:
					day_context['initials'] = initials(row.cells[6].value)
				day_context['category'] = row.cells[7].value

				showboards_context['DAYS'][day]['shows'][show].append(day_context)

	print "processing rundowns"
	for row in rundowns.rows:
		
		if row.cells[3].value=='SAMPLE DAY':
			break
		cast = row.cells[1].value
		day = row.cells[2].value
		on_board = row.cells[8].value
		item_type = row.cells[7].value
		print cast,day,on_board,item_type
		if day != None and day != 'date' and cast != None and item_type != 'Promo':
			day_obj = datetime.strptime(day,'%Y-%m-%d').date()
			day_of_week = day_obj.strftime('%A')
			date_str = day_obj.strftime('%b %d').lstrip("0").replace(" 0", " ")
			today_flag = (day_obj.strftime('%Y-%m-%d')==today)

			day_context = {}
			day_context['cast'] = cast
			day_context['status'] = row.cells[0].value
			day_context['story_slug'] = row.cells[3].value
			day_context['length'] = row.cells[4].value
			day_context['reporter'] = row.cells[5].value
			if row.cells[5].display_value != None:
				day_context['initials'] = initials(row.cells[5].display_value)
			day_context['editor'] = row.cells[6].value
			day_context['type'] = row.cells[7].value
			day_context['category'] = row.cells[11].value
			day_context['on_board'] = row.cells[8].value

			if day_obj >= two_days_ago and day_obj <= two_days_later:
				
				if day not in planning_context['DAYS']: 
					planning_context['DAYS'][day] = {'day_of_week': day_of_week, 'date_str':date_str, 'today':today_flag, 'cast_items':[], 'anchors':[], 'features': []}

				if row.cells[7].value == 'Feature':
					if not any(d['story_slug'] == row.cells[3].value for d in planning_context['DAYS'][day]['features']):
						planning_context['DAYS'][day]['features'].append(day_context)
				elif row.cells[7].value == 'Anchor':
					planning_context['DAYS'][day]['anchors'].append(day_context)
				elif not any(d['story_slug'] == row.cells[3].value for d in planning_context['DAYS'][day]['cast_items']):
					planning_context['DAYS'][day]['cast_items'].append(day_context)

	# for row in pegs.rows:
	# 	cast = row.cells[1]
	# 	reporter = row.cells[5]
	# 	day = row.cells[2]
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
	# 			context['status'] = row.cells[0]
	# 			context['story_slug'] = row.cells[3]
	# 			context['length'] = row.cells[4]
	# 			context['reporter'] = reporter
	# 			if reporter != None:
	# 				context['initials'] = initials(reporter)
	# 			context['editor'] = row.cells[6]
	# 			context['type'] = row.cells[7]
	# 			context['category'] = row.cells[10]

	# 			if row.cells[7] == 'Feature':
	# 				planning_context['DAYS'][day]['casts']['Features'].append(day_context)
	# 			else:
	# 				planning_context['DAYS'][day]['casts'][cast].append(context)
	print "processing features"
	for row in features.rows:
		
		cast = row.cells[1].value
		reporter = row.cells[5].value
		audio_type = row.cells[7].value
		day = row.cells[2].value

		if audio_type == 'Feature' and reporter != None and day != None:

			day_obj = datetime.strptime(day,'%Y-%m-%d').date()
			day_of_week = day_obj.strftime('%A')
			date_str = day_obj.strftime('%b %d').lstrip("0").replace(" 0", " ")

			if day_obj > tomorrow:
				context = {}
				context['day'] = day_obj
				context['date']= date_str
				context['status'] = row.cells[0].value
				context['cast'] = row.cells[1].value
				context['story_slug'] = row.cells[3].value
				context['format'] = row.cells[4].value
				context['reporter'] = reporter
				if row.cells[5].display_value != None:
					context['initials'] = initials(row.cells[5].display_value)
				elif reporter != None:
					context['initials'] = initials(reporter)
				context['editor'] = row.cells[6].value
				context['type'] = row.cells[7].value
				context['category'] = row.cells[10].value

				planning_context['FEATURES'].append(context)


	showboards_context['DAYS'] = OrderedDict(sorted(showboards_context['DAYS'].iteritems(), key=lambda x: x[0]))
	assignment_context['DAYS'] = OrderedDict(sorted(assignment_context['DAYS'].iteritems(), key=lambda x: x[0]))
	planning_context['DAYS'] = OrderedDict(sorted(planning_context['DAYS'].iteritems(), key=lambda x: x[0]))
	planning_context['FEATURES'] = sorted(planning_context['FEATURES'], key=lambda k: k['day'])

	remove_days(planning_context['FEATURES'])

	context = {'showboards':showboards_context, 'assignments': assignment_context, 'planning': planning_context}

	file_location = "%s/static/smartsheet.json" % FILE_DIR
	
	with open(file_location, 'w') as outfile:
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