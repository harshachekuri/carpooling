import datetime
from bson import ObjectId
from flask import render_template,Flask,request,session
import pymongo
import smtplib

app=Flask(__name__)
app.secret_key='99009'

client=pymongo.MongoClient('mongodb+srv://chiru:chiru@cluster0.pgk2x.mongodb.net/?retryWrites=true&w=majority')

@app.route('/')
def first():
  return render_template('main.html')

@app.route('/logout_driver',methods=['get'])
def logout_driver():
	session.pop('e')
	return render_template('main.html')

@app.route('/rider_reg')
def give():
  return render_template('rider_reg.html')

@app.route('/pass_reg')
def book():
  return render_template('pass_reg.html')

@app.route('/loginp')
def login2():
  return render_template('loginP.html')

@app.route('/loginr')
def login1():
  return render_template('loginR.html')

@app.route('/offerride')
def offerride():
  return render_template('offerride.html')

@app.route('/bookride')
def bookride():
  return render_template('bookingride.html')

@app.route('/book',methods=['post'])
def bookaride():
  i={}
  i['_id']=ObjectId(request.form['id'])
  to=request.form['mail']
  m=session['e']
  k={}
  k['rider']=session['e']
  k['bid']=request.form['bid']
  k['pick']=request.form['pick']
  k['drop']=request.form['drop']
  c=client['project']['soanddes']
  c.update_one({"_id":i['_id']},{'$push':{'requests':k}})
  data=c.find()
  data=list(data)
  message="the passenger "+m+" is requested for your ride from "+k['pick']+' to '+k['drop']
  server =smtplib.SMTP('smtp.gmail.com',587)
  server.starttls()
  server.login('ridenshare.carpooling@gmail.com','rhmflcqneosupijc')
  server.sendmail('ridenshare.carpooling@gmail.com',to,message)
  return render_template('passenger_home.html',data=reversed(data),email=session['e'])

@app.route('/backhome')
def backhome():
  c=client['project']['soanddes']
  data=c.find()
  dcopy=[]
  for i in data:
    if i['driver'] == session['e']:
      dcopy.append(i)
  return render_template('riderhome.html',data=dcopy)

@app.route('/backphome' ,methods=['get'])
def backpass():
  c=client['project']['soanddes']
  data=c.find()
  return render_template('passenger_home.html',data=data,email=session['e'])

@app.route('/booked')
def booked():
  c=client['project']['soanddes']
  data=c.find()
  d=[]
  l=[]
  for i in data:
    for j in i['requests'][:]:
      if 'rider' in j and j['rider']==session['e']:
        d.append(i)
    for k in i['passengers'][:]:
      if 'rider' in k and k['rider']==session['e']:
        l.append(i)
  return render_template('booked.html',data1=d,data2=l)

@app.route('/pass_reg_verify',methods=['POST'])
def details():
  name=request.form['name']
  email=request.form['email']
  age=request.form['age']
  password=request.form['password']
  sex=request.form['sex']
  k={}
  k['name']=name
  k['email']=email
  k['age']=age
  k['sex']=sex
  k['password']=password
  c=client['project']['bookingdetails']
  data=c.find()
  for i in data:
    if i['name']==name or i['email']==email:
      return render_template('pass_reg.html',res='Exisisting User')
  c.insert_one(k)
  return render_template('loginP.html')


@app.route('/pass_log_verify',methods=['POST'])
def login():
  email=request.form['email']
  password=request.form['password']  
  c=client['project']['bookingdetails']
  data=c.find() 
  for i in data:
    if i['email']==email and i['password']==password:
      session['e']=email
      c=client['project']['soanddes']
      data=c.find()
      data=list(data)
      return render_template('passenger_home.html',data=reversed(data),email=email)
  return render_template('loginP.html',ack='invalid login please check your details')

@app.route('/rider_log_verify',methods=['POST'])
def rlogin():
  email=request.form['email']
  password=request.form['password']  
  vno=request.form['vno']
  c=client['project']['riderdetails']
  data=c.find()
  c2=client['project']['soanddes']
  data1=c2.find()
  for i in data:
      if i['email']==email and i['password']==password and i['vno']==vno:
            session['e']=email
            dcopy=[]
            for i in data1:
              if i['driver'] == email:
                dcopy.append(i)
            return render_template('riderhome.html',data=dcopy)
  return render_template('loginR.html',res='invalid login please check your details') 

@app.route('/acc',methods=['get'])
def acc():
  i={}
  i['_id']=ObjectId(request.args.get('id'))
  rider=request.args.get('rid')
  c=client['project']['soanddes']
  data1=c.find()
  for l in data1:
    if l['_id'] == i['_id']:
      data=l['requests']
  for o in data:
    if o['rider']==rider:
      pp=o
  c.update_one({"_id":i['_id']},{'$pull':{'requests':{'rider':pp['rider']}}})
  c.update_one({'_id':i['_id']},{'$push':{'passengers':pp}})
  c.update_one({"_id":i['_id']},{'$inc':{'seats':-1}})
  data1=c.find()
  dcopy=[]
  for i in data1:
    if i['driver'] == session['e']:
      dcopy.append(i)
  to=rider    
  message="Your request for the ride from "+pp['pick']+" to "+pp['drop']+"is accepted by the raider "+session['e']
  server =smtplib.SMTP('smtp.gmail.com',587)
  server.starttls()
  server.login('rideNshare.carpooling@gmail.com','rhmflcqneosupijc')
  server.sendmail('rideNshare.carpooling@gmail.com',to,message)
  return render_template('riderhome.html',data=dcopy)

  
@app.route('/rider_reg_verify',methods=['POST','get'])
def ak():
  name=request.form['name']
  email=request.form['email']
  age=request.form['age']
  password=request.form['password']
  vno=request.form['vno']
  vname=request.form['vname']
  sex=request.form['sex']
  k={}
  k['name']=name
  k['email']=email
  k['age']=age
  k['sex']=sex
  k['password']=password
  k['vname']=vname
  k['vno']=vno
  c=client['project']['riderdetails']
  data=c.find()
  for i in data:
    if i['name']==name or i['email']==email:
      return render_template('rider_reg.html',res='Exisiting User')
  c.insert_one(k)
  return render_template('loginR.html')



@app.route('/detailssd',methods=['POST'])
def sd():
  source=request.form['source']
  destination=request.form['destination']
  date=request.form['date']
  time=int(request.form['time'])
  seats=request.form['seats']
  c=client['project']['soanddes']
  al=c.find()
  if 0 > time or time >23:
    return render_template('offerride.html',ack="Invalid Time")
  for i in al:
    if date==i['date'] and time ==i['time']:
      return render_template('offerride.html',ack="You have already Registered to give a Ride at mentioned date and time")
  if int(seats) <=0:
    return render_template('offerride.html',ack="No of seats must be greater than 0")
  k={}
  k['driver']=session['e']
  k['source']=source
  k['destination']=destination
  k['date']=date
  k['time']=time
  k['seats']=int(seats)
  k['passengers']=[]
  k['requests']=[]
  c.insert_one(k)
  c=client['project']['soanddes']
  data=c.find()
  dcopy=[]
  for i in data:
    if i['driver'] == session['e']:
      dcopy.append(i)
  return render_template('riderhome.html',data=dcopy)

@app.route('/cancel',methods=['get'])
def cancel():
  i={}
  i['_id']=ObjectId( request.args.get('id'))
  c=client['project']['soanddes']
  c.delete_one(i)
  data=c.find()
  dcopy=[]
  for i in data:
    if i['driver'] == session['e']:
      dcopy.append(i)
  return render_template('riderhome.html',data=dcopy)


@app.route('/can1',methods=['get'])
def can1():
  i=ObjectId( request.args.get('id'))
  c=client['project']['soanddes']
  c.update_one({"_id":i},{'$pull':{'requests':{'rider':session['e']}}})
  data=c.find()
  data=list(data)
  return render_template('passenger_home.html',data=reversed(data),email=session['e'])


@app.route('/can2',methods=['get'])
def can2():
  i={}
  i['_id']=ObjectId( request.args.get('id'))
  i['mail']=request.args.get('rid')
  to=i['mail']
  c=client['project']['soanddes']
  c.update_one({"_id":i['_id']},{'$pull':{'requests':{'rider':i['mail']}}})
  data=c.find()
  email=session['e']
  dcopy=[]
  for i in data:
    if i['driver'] == email:
      dcopy.append(i)
  server =smtplib.SMTP('smtp.gmail.com',587)
  server.starttls()
  server.login('ridenshare.carpooling@gmail.com','rhmflcqneosupijc')
  message="Your request is cancelled by "+email
  server.sendmail('ridenshare.carpooling@gmail.com',to,message)
  return render_template('riderhome.html',data=dcopy,email=session['e'])



@app.route('/req',methods=['get'])
def requests():
  i={}
  i['_id']=ObjectId(request.args.get('id'))
  c=client['project']['soanddes']
  data=c.find_one({'_id':i['_id']})
  c=client['project']['riderdetails']
  details=c.find_one({'email':data['driver']})
  return render_template('request.html',data=data,details=details)

@app.route('/logout_pass')
def logout_pass():
  session.pop('e')
  return render_template('main.html')


from apscheduler.schedulers.background import BackgroundScheduler


def test_job():
    date=int(datetime.datetime.now().strftime("%Y%m%d"))
    time=int(datetime.datetime.now().strftime("%H"))
    c=client['project']['soanddes']
    data=c.find()
    for i in data:
      dc=i['date']
      d=int("".join(i['date'].split('-')))
      t=i['time']
      if d>date:
        continue
      elif d==date and t > time:
        continue
      else:
        da=i['date']
        ti=i['time']
        c.delete_one({'date':da,'time':ti})

scheduler = BackgroundScheduler()
job = scheduler.add_job(test_job, 'interval', seconds=10)
scheduler.start()

if __name__=='__main__':
  app.run()