import os
import time
import datetime
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

#database that store users' plan
class Plans(db.Model):
	plan = db.StringProperty()

# main page, display a form to ask users for information
class MainPage(webapp.RequestHandler):
	def get(self):
		# login to google calendar
		user = users.get_current_user()
		if user:
			# already logged in
			# get users' plan
			plan_entity = Plans.get_or_insert(user.user_id(),plan='1,2,4,7,15,30,60,100')
			plan_str = plan_entity.plan
			# show form
			template_values = {
				'plan': plan_str,
				'today': datetime.date.today()
			}
			path = os.path.join(os.path.dirname(__file__), 'index.html')
			self.response.out.write(template.render(path, template_values))
		else:
			# go to login page
			self.redirect(users.create_login_url(self.request.uri))


# get submitted information and add events to calendar
class AddToCalendar(webapp.RequestHandler):
	def get(self):
		# get information
		plan_str = self.request.get('plan')
		start_date_str = self.request.get('start_date')
		summary = self.request.get('summary')
		description = self.request.get('description')
		# calculate review days
		start_date_str_array = start_date_str.split('-')
		start_date = datetime.datetime(int(start_date_str_array[0]),int(start_date_str_array[1]),int(start_date_str_array[2]))
		plan_str_array = plan_str.split(',')
		review_days = [(start_date + datetime.timedelta(days=int(x))) for x in plan_str_array]
		# login to google calendar
		user = users.get_current_user()
		if user:
			# already logged in
			# save new plan
			plan_entity = Plans.get_or_insert(user.user_id(),plan='1,2,4,7,15,30,60,100')
			plan_entity.plan = plan_str
			plan_entity.put()
			# add to calendar
		else:
			# go to login page
			self.redirect(users.create_login_url(self.request.uri))
		# show success
		review_days_str = [str(x.date()) for x in review_days]
		template_values = {
			'review_days': review_days_str
		}
		path = os.path.join(os.path.dirname(__file__), 'success.html')
		self.response.out.write(template.render(path, template_values))
		

application = webapp.WSGIApplication([('/', MainPage),('/add_to_calendar',AddToCalendar)])

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
	main()