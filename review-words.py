#==================================imports====================================================================
import os
import time
import datetime
import gflags
import httplib2
from google.appengine.api import users
from google.appengine.api import memcache
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app
from oauth2client.appengine import OAuth2Decorator
from apiclient.discovery import build


#===============================auth related==================================================================
decorator = OAuth2Decorator(
	client_id='785871267070-bm42i94l35chflm8s1aeus0pfrqqkssg.apps.googleusercontent.com',
	client_secret='eU6tFA1N5fCbDR1ACbejEUsl',
	scope='https://www.googleapis.com/auth/calendar',
	user_agent='review-words/1.0')

http = httplib2.Http(memcache)
service = build(
	serviceName='calendar', 
	version='v3', http=http,
	developerKey='AIzaSyC0CdFe4FZDeF06SAf6UKkko90NAZ8EZbU')


#=================================databases===================================================================
#database that store users' plan
class Plans(db.Model):
	plan = db.StringProperty()


#==============================RequestHandlers================================================================
# main page, display a form to ask users for information
class MainPage(webapp.RequestHandler):
	
	@decorator.oauth_required
	def get(self):
		# get users' plan
		user = users.get_current_user()
		plan_entity = Plans.get_or_insert(user.user_id(),plan='1,2,4,7,15,30,60,100')
		plan_str = plan_entity.plan
		# show form
		template_values = {
			'plan': plan_str,
			'today': datetime.date.today()
		}
		path = os.path.join(os.path.dirname(__file__), 'index.html')
		self.response.out.write(template.render(path, template_values))

# get submitted information and add events to calendar
class AddToCalendar(webapp.RequestHandler):
	
	@decorator.oauth_required
	def get(self):
		# get information
		plan_str = self.request.get('plan')
		start_date_str = self.request.get('start_date')
		summary = self.request.get('summary')
		description = self.request.get('description')
		# calculate review days
		start_date_str_array = start_date_str.split('-')
		start_date = datetime.datetime(int(start_date_str_array[0]),
					       int(start_date_str_array[1]),
					       int(start_date_str_array[2]))
		plan_str_array = plan_str.split(',')
		review_days = [(start_date + datetime.timedelta(days=int(x))) for x in plan_str_array]
		# save new plan
		user = users.get_current_user()
		plan_entity = Plans.get_or_insert(user.user_id(),plan='1,2,4,7,15,30,60,100')
		plan_entity.plan = plan_str
		plan_entity.put()
		# add to calendar
		event = {
			'summary': summary,
			'start': {
				'dateTime': '2011-06-03T10:00:00.000-07:00',
				'timeZone': 'America/Los_Angeles'
			},
			'end': {
				'dateTime': '2011-06-03T10:25:00.000-07:00',
				'timeZone': 'America/Los_Angeles'
			},
		}
		service.events().insert(calendarId='primary', body=event).execute()
		# show success
		review_days_str = [str(x.date()) for x in review_days]
		template_values = {
			'review_days': review_days_str
		}
		path = os.path.join(os.path.dirname(__file__), 'success.html')
		self.response.out.write(template.render(path, template_values))
		

#====================================main======================================================================
application = webapp.WSGIApplication([('/', MainPage),('/add_to_calendar',AddToCalendar)])

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
	main()