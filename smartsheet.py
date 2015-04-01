import smartsheetclient
from collections import OrderedDict
from datetime import datetime, date, timedelta
import os

def make_context():
	today = datetime.today().strftime('%Y-%m-%d')
	two_days_ago = (datetime.today()-timedelta(days=4)).strftime('%Y-%m-%d')

	token = os.getenv('SMARTSHEET_TOKEN')

	client = smartsheetclient.SmartsheetClient(token)
	client.connect()
	sheet_list = client.fetchSheetList()

	showboardsid = '2812472127186820'

	sheet = client.fetchSheetById(showboardsid)
	context = {}
	context['DAYS'] = OrderedDict()
	columns = [col.title for col in sheet.columns]

	for row in sheet.rows:
		show  = row[0]
		if show != None:
			day = row[3]
			day_obj = datetime.strptime(row[3],'%Y-%m-%d')
			day_of_week = day_obj.strftime('%A')
			date_str = day_obj.strftime('%b %d').lstrip("0").replace(" 0", " ")
			
			if day not in context['DAYS']: 
				context['DAYS'][day] = {'day_of_week': day_of_week, 'date_str':date_str, 'shows':{}}
			if show not in context['DAYS'][day]['shows']: 
				context['DAYS'][day]['shows'].update({show:[]})

			day_context = {}
			day_context['show'] = show
			day_context['status'] = row[1]
			day_context['segment']  = row[2]
			day_context['story_slug']  = row[4]
			day_context['segment_type']  = row[5]
			day_context['reporter']  = row[6]
			day_context['category']  = row[7]

			context['DAYS'][day]['shows'][show].append(day_context)

	context['DAYS'] = OrderedDict(sorted(context['DAYS'].iteritems(), key=lambda x: x[0]))
	return context