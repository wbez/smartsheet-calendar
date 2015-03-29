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
	context['SHOWS'] = OrderedDict()
	columns = [col.title for col in sheet.columns]

	for row in sheet.rows:
		show  = row[0]
		if show != None:
			day = row[3]
			#day = datetime.strptime(row[3],'%Y-%m-%d')
			
			if day not in context['SHOWS']: 
				context['SHOWS'][day] = {}
			if show not in context['SHOWS'][day]: 
				context['SHOWS'][day][show] = []
			
			day_context = {}
			day_context['show'] = show
			day_context['status'] = row[1]
			day_context['segment']  = row[2]
			day_context['story_slug']  = row[4]
			day_context['segment_type']  = row[5]
			day_context['reporter']  = row[6]
			day_context['category']  = row[7]

			context['SHOWS'][day][show].append(day_context)

	return context