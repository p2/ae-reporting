import bottle
from bottle import static_file

application = bottle.Bottle()


@application.route('/')
def index():
	return "Hello World! AppFog Python Support"


@application.route('/authorize')
def authorize():
	try:
		return static_file('authorize.html', root='static')
	except Exception, e:
		return 'Not possible: %s' % e

