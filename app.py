from flask import Flask, request, json,send_file
from flaskext.mysql import MySQL
from flask_cors import CORS, cross_origin
import datetime
import os
from PIL import Image
import base64
import cStringIO
import PIL.Image

app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
app.config.from_pyfile('dbapp.py')
mysql = MySQL()
mysql.init_app(app)
global dbcon
dbcon = None

@app.route("/")
def main():
    #upldimg()
    return send_file('templates/Home.html')


@app.route("/get_nb", methods=['GET'])
def get_nb():
    mtype="a0"
    entries = []
    sql1 = "SELECT * FROM NB_Sched order by ID desc LIMIT 1"
    fdt=""
    tdt=""
    srow1, stat1 = dboper(sql1, True)
    if stat1:
        for row1 in srow1:
            fdt = row1[1]
            tdt = row1[2]
    if fdt != "" and tdt != "":
        dtFrDate,dtToDate = uhfgetFrToDate(fdt,tdt)
        sql = "SELECT * FROM NB_Info order by ID"

        srow, stat = dboper(sql, True)
        if stat:
            for row in srow:
                nbid = str(row[0])
                dtformat = row[3]
                datetimeobject2 = datetime.datetime.strptime(dtformat,'%d/%m/%Y %H:%M:%S')
                dtbet = datetimeobject2.date()
                if (dtFrDate <= dtbet) and (dtbet <= dtToDate):
                    sql1 = "select * from NB_Type where nbid = "+str(nbid)
                    srow2, stat = dboper(sql1, True)
                    if stat:
                        if srow2 is not None:
                            for rw in srow2:
                                mtype = rw[1]
                                getcurimg(mtype,nbid)

                    dict = { 'nbid': row[0], 'SchName': row[1], 'Subj': row[2],'TimeStamp': row[3], 'Msg': row[4], 'mtype': mtype }
                    entries.append(dict)

    print entries
    currentries = []
    if len(entries) > 0:
        currentries.append(entries[0])
    retdict = { 'starg': 'get_nb',  'entries': entries, 'fdt': fdt,'tdt': tdt,'currentries':currentries}
    return json.dumps(retdict)


@app.route("/get_cdt", methods=['GET'])
def get_cdt():
    today = datetime.datetime.now()
    newformat = today.strftime('%d/%m/%Y')
    newformat1 = today.strftime('%H:%M:%S')
    retdict = { 'starg': 'get_cdt', 'cdt': newformat , 'ctm': newformat1 }
    return json.dumps(retdict)


@app.route('/upldimg', methods=['POST'])
@cross_origin()
def upldimg():
    if os.path.exists('static/uploads/TCET.jpg'):
        os.remove('static/uploads/TCET.jpg')
    request.files['Imgname'].save('static/uploads/TCET.jpg')
    sql1 = "select * from NB_Info order by ID desc Limit 1"
    srow, stat = dboper(sql1, False)
    if stat:
        if srow:
            nbid = srow[0]
            con = mysql.connect()
            image = Image.open('static/uploads/TCET.jpg')
            blob_value = open('static/uploads/TCET.jpg', 'rb').read()
            sql = "INSERT INTO nbd_image(nbimage,nbid) VALUES(%s,"+str(nbid)+")"
            args = (blob_value)
            cursor=con.cursor()
            val = 0
            sel = "FAIL"
            try:
                cursor.execute(sql,args)
                con.commit()
                con.close()
                sel = "SUCCESS"
                val = 1
            except Exception,e:
                print e
                con.close()
                sel = "FAIL"
                val = 0
                print "Exception has happened"
    retdict = { 'success': val, 'message': sel }
    return json.dumps(retdict)


@app.route("/getNBMsg", methods=['POST'])
@cross_origin()
def getNBMsg():
    val = 0
    sel = "FAIL"
    data1 = request.get_json(silent=True)
    print data1
    con = mysql.connect()
    cursor = con.cursor()
    fdt = data1["FromDt"]
    tdt = data1["ToDt"]
    if data1:
        try:
            cursor.execute("insert into NB_Info(SchName,Subj,TimeStamp,Msg) VALUES('"+data1["SchName"]+"','"+data1["Subj"]+"','"+data1["TimeStamp"]+"','"+data1["Msg"]+"')")
            cursor.execute("delete from NB_Sched")
            cursor.execute("insert into NB_Sched(FromDt,ToDt) VALUES('"+fdt+"','"+tdt+"')")
            con.commit()
            sql1 = "select * from NB_Info order by ID desc Limit 1"
            srow, stat = dboper(sql1, False)
            if stat:
                if srow:
                    nbid = str(srow[0])
                    cursor.execute("insert into NB_Type(MsgType,nbid) VALUES('"+data1["MsgType"]+"'," + nbid + ")")
            con.commit()
            dtFrDate,dtToDate = uhfgetFrToDate(fdt,tdt)
            sql9 = "SELECT * FROM NB_Info order by ID"
            srow9, stat9 = dboper(sql9, True)
            if stat9:
                for row9 in srow9:
                    nbid = str(row9[0])
                    dtformat = row9[3]
                    datetimeobject2 = datetime.datetime.strptime(dtformat,'%d/%m/%Y %H:%M:%S')
                    dtbet = datetimeobject2.date()
                    if (dtFrDate <= dtbet) and (dtbet <= dtToDate):
                        pass
                    else:
                        if os.path.exists('static/nbdimg/{}.jpg'.format(nbid)):
                            os.remove('static/nbdimg/{}.jpg'.format(nbid))
                        cursor.execute("delete from NB_Info where ID = "+nbid)
                        cursor.execute("delete from NB_Type where nbid = "+nbid)
                        cursor.execute("delete from nbd_image where nbid = "+nbid)
            con.commit()
            sel = "SUCCESS"
            val = 1
            cursor.close()
            con.close()
        except Exception,e:
            print e
            con.close()
            sel = "FAIL"
            val = 0
            print "Exception has happened"
    retdict = { 'success': val, 'message': sel }
    return json.dumps(retdict)

def getcurimg(mtype,nbid):
    if mtype == 'a1' or mtype == 'a2':
        global dbcon
        get_db()
        try:
            cur = dbcon.cursor()
            #open file and write into.
            imnm = 'static/nbdimg/{}.jpg'.format(nbid)
            print imnm
            with open(imnm,"wb") as output_file:
                row_cnt = cur.execute("SELECT nbimage FROM nbd_image WHERE nbid="+str(nbid))
                if row_cnt > 0:
                    ablob = cur.fetchone()
                    output_file.write(ablob[0])
            cur.close()
            close_db_connection()
        except Exception,e:
            print e
            close_db_connection()
    return

def uhfgetFrToDate(frdt,trdt):
    datetimeobject = datetime.datetime.strptime(frdt,'%d/%m/%Y')
    dtFrDate = datetimeobject.date()
    datetimeobject1 = datetime.datetime.strptime(trdt,'%d/%m/%Y')
    dtToDate = datetimeobject1.date()
    return dtFrDate,dtToDate


def dboper(qry, bval):
    global dbcon
    get_db()
    try:
        cursor = dbcon.cursor()
        rows_count = cursor.execute(qry)
        if rows_count > 0:
            if bval:
                row = cursor.fetchall()
            else:
                row = cursor.fetchone()
            stat = True
        else:
            stat = False
            row = None
    except Exception,e:
        print e
        stat = False
        row = None
    close_db_connection()
    return row, stat


def get_db():
    global dbcon
    if not dbcon:
        dbcon = mysql.connect()
    else:
        if dbcon and not dbcon.open:
            dbcon = mysql.connect()


# Closes dbconnection object if it is opened
def close_db_connection():
    global dbcon
    if dbcon and dbcon.open:
        dbcon.close()
        dbcon = None


if __name__ == "__main__":
    #app.run(debug = True)
    app.run(debug = True,host='0.0.0.0', port=5001)