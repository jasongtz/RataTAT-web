# WebApp using Bottle

import os
import bottle as bt
from bottle import route, run, template, request, get, post
import modularui as m

app = bt.Bottle()

genius = m.declaregenius(m.readgenius())

@app.route("/static/css/<filename>")
def stylesheets(filename):
	return bt.static_file(filename, root='./static/css')
@app.route("/static/img/<filename>")
def stylesheets2(filename):
	return bt.static_file(filename, root='./static/img')
@app.route("/static/fonts/<filename>")
def stylesheets3(filename):
	return bt.static_file(filename, root='./static/fonts')


@app.route("/bar")
def bar_index():
	return template("templates/bar", genius=m.declaregenius(m.readgenius()), \
		to_print=m.displaymessage(), status=m.get_status(), apptitle=m.apptitle)


@app.route("/confirmd")
def quoted():
	current_status = m.getcurrentstatus()
	to_print = m.quote_display(current_status[0], current_status[1], 
		current_status[2], current_status[3], m.readgenius())	
	return template("templates/confirmd", genius=m.declaregenius(m.readgenius()), \
		to_print=to_print, status=m.get_status(), apptitle=m.apptitle)

@app.route("/confirmb")
def quoteb():
	current_status = m.getcurrentstatus()
	to_print = m.quote_battery(current_status[0], current_status[1], m.readgenius())	
	return template("templates/confirmb", genius=m.declaregenius(m.readgenius()), \
		to_print=to_print, status=m.get_status(), apptitle=m.apptitle)

@app.route("/d")
def action_d():
	m.display.add()
	return template("templates/bar", genius=m.declaregenius(m.readgenius()), \
		to_print=m.displaymessage(), status=m.get_status(), apptitle=m.apptitle)

@app.route("/b")
def action_b():
	m.battery.add()
	return template("templates/bar", genius=m.declaregenius(m.readgenius()), \
		to_print=m.displaymessage(), status=m.get_status(), apptitle=m.apptitle)


@app.route("/gr")
def gr_index():
	return template("templates/gr", genius=m.declaregenius(m.readgenius()), \
		 to_print=m.displaymessage(), status=m.get_status(), apptitle=m.apptitle)

@app.route("/dc")
def action_dc():
	if m.getcurrentstatus()[1] > 0:
		m.calib.add()
	return template("templates/gr", genius=m.declaregenius(m.readgenius()), \
		to_print=m.display.remove(), status=m.get_status(), apptitle=m.apptitle)
	
@app.route("/df")
def action_df():
	if m.getcurrentstatus()[2] > 0:
		return template("templates/gr", genius=m.declaregenius(m.readgenius()), \
			to_print=m.fail.add(), status=m.get_status(), apptitle=m.apptitle)
	else:
		return template("templates/gr", genius=m.declaregenius(m.readgenius()), \
			to_print="Error!", status=m.get_status(), apptitle=m.apptitle)
		
	
@app.route("/nd")
def action_dc():	
	return template("templates/gr", genius=m.declaregenius(m.readgenius()), \
		to_print=m.calib.remove(), status=m.get_status(), apptitle=m.apptitle)

@app.route("/nb")
def action_dc():
	
	return template("templates/gr", genius=m.declaregenius(m.readgenius()), \
		to_print=m.battery.remove(), status=m.get_status(), apptitle=m.apptitle)

@app.route("/grd")
def action_d():
	
	return template("templates/gr", genius=m.declaregenius(m.readgenius()), \
		to_print=m.display.add(), status=m.get_status(), apptitle=m.apptitle)

@app.route("/grb")
def action_b():
	
	return template("templates/gr", genius=m.declaregenius(m.readgenius()), \
		to_print=m.battery.add(), status=m.get_status(), apptitle=m.apptitle)


@app.route("/genius<num>")
def geniusnum(num):
	return template("templates/gr", genius=m.setgenius(num), \
		 to_print=m.displaymessage(), status=m.get_status(), apptitle=m.apptitle)

#@app.route("/feedback")

@app.get("/feedback")
def form():
	return template("templates/feedback", apptitle=m.apptitle)

@app.post("/feedback")
def submit():
	m.sendfeedback(request.forms.get("feedbacktext"))
	return template("templates/launch", genius=m.declaregenius(m.readgenius()), \
		apptitle=m.apptitle)


@app.route("/")
def undeclared_index():
	return template("templates/launch", genius=m.declaregenius(m.readgenius()), \
		apptitle=m.apptitle)


bt.debug(True)
run(app, reloader=True, host="0.0.0.0", port=8080)
	