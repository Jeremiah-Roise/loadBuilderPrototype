import sqlite3
from types import MethodType
from typing import Dict

from flask import Flask, redirect, render_template, request

db = sqlite3.connect("loadBuilder.sqlite3",check_same_thread=False)
db.execute("""
    CREATE TABLE IF NOT EXISTS Opportunitys (
    projectID INTEGER PRIMARY KEY,
	projectName TEXT,
	customerName TEXT,
	email TEXT,
	Location TEXT,
	notes TEXT,
	isOpportunityOnly TEXT);
    """)
db.execute("""
    CREATE TABLE IF NOT EXISTS Projects (projectID INTEGER NOT NULL,
	projectName TEXT,
	customerName TEXT,
	email TEXT,
	Location TEXT,
	notes TEXT,
	FOREIGN KEY (projectID) REFERENCES Opportunitys (projectID));
    """)
db.execute("""
    CREATE TABLE IF NOT EXISTS Bases (
	ID INTEGER NOT NULL PRIMARY KEY UNIQUE,
	projectID INTEGER NOT NULL,
	baseName TEXT,
	description TEXT,
	buildingType TEXT,
    price INTEGER,
    status TEXT,
	FOREIGN KEY (projectID) REFERENCES Opportunitys (projectID));
    """)

db.execute("""
    CREATE TABLE IF NOT EXISTS Alts (
	ID INTEGER NOT NULL PRIMARY KEY UNIQUE,
	projectID INTEGER NOT NULL,
	altName TEXT,
	description TEXT,
    price INTEGER,
    status TEXT,
	FOREIGN KEY (projectID) REFERENCES Opportunitys (projectID));
    """)

db.execute("""
    CREATE TABLE IF NOT EXISTS altFloors (
    ID INTEGER PRIMARY KEY NOT NULL UNIQUE,
	altID INTEGER NOT NULL,
    projectID INTEGER NOT NULL,
    floorNumber INTEGER NOT NULL,
	FOREIGN KEY (altID) REFERENCES Alts (ID),
	FOREIGN KEY (projectID) REFERENCES Projects (projectID));
    """)

db.execute("""
    CREATE TABLE IF NOT EXISTS BaseAlts (
    ID INTEGER PRIMARY KEY NOT NULL UNIQUE,
	baseID INTEGER NOT NULL,
    altID INTEGER NOT NULL,
	FOREIGN KEY (baseID) REFERENCES Bases (ID),
	FOREIGN KEY (altID) REFERENCES Alts (ID));
    """)

db.execute("""
    CREATE TABLE IF NOT EXISTS altFloorLoads (
    ID INTEGER NOT NULL,
    loadType INTEGER NOT NULL,
	FOREIGN KEY (ID) REFERENCES altFloors (ID),
	FOREIGN KEY (loadType) REFERENCES LoadTypes (ID)
    );
    """)

db.execute("""
    CREATE TABLE IF NOT EXISTS Floors (
    ID INTEGER PRIMARY KEY NOT NULL,
	baseID INTEGER NOT NULL,
    projectID INTEGER NOT NULL,
    floorNumber INTEGER NOT NULL,
	FOREIGN KEY (baseID) REFERENCES Bases (ID),
	FOREIGN KEY (projectID) REFERENCES Projects (projectID));
    """)

db.execute("""
    CREATE TABLE IF NOT EXISTS LoadTypes (
    ID INTEGER PRIMARY KEY NOT NULL UNIQUE,
    loadName TEXT UNIQUE NOT NULL,
    description TEXT);
    """)

db.execute("""
    CREATE TABLE IF NOT EXISTS FloorLoads (
    ID INTEGER NOT NULL,
    loadType INTEGER NOT NULL,
	FOREIGN KEY (ID) REFERENCES Floors (ID),
	FOREIGN KEY (loadType) REFERENCES LoadTypes (ID)
    );
    """)
db.close()



def newAlt(project_id, alt_name, load_data_list):
    data = request.form.to_dict(flat=False)
    print(data)
    db = sqlite3.connect("loadBuilder.sqlite3",check_same_thread=False)
    cur = db.execute("INSERT INTO Alts(projectID, altName) VALUES (? ,?);", (project_id, alt_name))
    alt_id = cur.lastrowid
    for base_id, floor_number, load_id in load_data_list:
        # tie the new alts to their respective bases
        cur.execute("INSERT INTO BaseAlts(baseID, altID) VALUES (? ,?);", (base_id, alt_id))
        # tie a floor to the alts
        cur.execute("INSERT INTO altFloors(altID, projectID, floorNumber) VALUES (?, ?, ?);", (alt_id,project_id,floor_number))
        # tie the loads to the floor
        cur.execute("INSERT INTO altFloorLoads(ID, loadType) VALUES (?, ?);", (cur.lastrowid,load_id))
        db.commit()
    return alt_id




def newBase(project_id, base_name, description, building_type, price, status):
    data = request.form.to_dict(flat=False)
    db = sqlite3.connect("loadBuilder.sqlite3",check_same_thread=False)
    cur = db.execute("INSERT INTO Bases(projectID, baseName, description, buildingType) VALUES (? ,? ,? ,?);", (project_id, base_name, description, building_type))
    base_id = cur.lastrowid
    db.commit()
    db.close()
    return base_id

def addFloorsToBase(base_id, project_id):
    data = request.form.to_dict(flat=False)
    db = sqlite3.connect("loadBuilder.sqlite3",check_same_thread=False)
    db.commit()
    for key, value in zip(data.keys(),data.values()):
        if key.isdigit():
            cur = db.execute("INSERT INTO Floors(baseID, projectID, floorNumber) VALUES (? ,? ,?);", (base_id, project_id, key))
            floor_row_id = cur.lastrowid
            for load_id in value:
                cur.execute("INSERT INTO FloorLoads(ID,loadType) VALUES (?,?)",(floor_row_id,load_id))
    db.commit()
    db.close()



newfloorindex = 0

def create_application():
    app = Flask(__name__)


    def getfrom_db_as_dict_list(query):
        colname = [ d[0] for d in query.description ]
        result_list = [ dict(zip(colname, r)) for r in query.fetchall() ]
        return result_list


    @app.route("/")
    def index():
        # Convert to list of dicts.
        db = sqlite3.connect("loadBuilder.sqlite3",check_same_thread=False)
        query = db.execute("SELECT * FROM Opportunitys;")
        result_list = getfrom_db_as_dict_list(query)

        return render_template('opportunityList.html',projects=result_list)

    @app.route("/new",methods=['GET','POST'])
    def new_opportunity():
        if request.method == "POST":
            for value in request.form.values():
                print(value)
            return redirect("/")

            
        return render_template('opportunityNew.html')


    @app.route("/opportunity/<int:project_id>/")
    def opportunity_view(project_id):
        # Select from database and display it
        db = sqlite3.connect("loadBuilder.sqlite3")
        query = db.execute("SELECT * FROM Opportunitys Where projectID==?;", (int(project_id),))
        result_list = getfrom_db_as_dict_list(query)
        print(result_list[0])

        db = sqlite3.connect("loadBuilder.sqlite3")
        q2 = db.execute("SELECT * FROM Projects Where projectID==?;", (int(project_id),))
        r2 = getfrom_db_as_dict_list(q2)
        return render_template('opportunityOverview.html',opportunity=result_list[0],projects=r2)



    @app.route("/opportunity/<int:project_id>/addproject",methods=['GET','POST'])
    def addProjectToOpportunity(project_id):
        if request.method == "POST":
            data = request.form
            db = sqlite3.connect("loadBuilder.sqlite3",check_same_thread=False)
            print(data)
            db.execute("INSERT INTO Projects( projectID , projectName , customerName , email , Location , notes) VALUES (? ,? ,? ,? ,? ,?);", (project_id, data['name'], data['customer'], data['email'], data['buildingtype'], data['notes']))
            db.commit()
            db.close()
            return redirect("/opportunity/<int:project_id>/")
        return render_template('projectNew.html', projectID=project_id)


    @app.route("/opportunity/<int:project_id>/newbase",methods=['GET','POST','PUT','DELETE'])
    def addBase(project_id):
        global newfloorindex
        if request.method == "POST":
            data = request.form.to_dict(flat=False)
            base_id = newBase(project_id,data['name'][0],data["description"][0],data["type"][0],None,None)
            addFloorsToBase(base_id,project_id)
            return redirect("/opportunity/" + str(project_id))

        # add floor to base
        if request.method == "PUT":
            newfloorindex += 1
            db = sqlite3.connect("loadBuilder.sqlite3")
            query = db.execute("SELECT ID, loadName FROM LoadTypes;")
            result_list = getfrom_db_as_dict_list(query)
            return render_template("floorConfig/floorForm.html", project_id=project_id, floorNumber=str(newfloorindex),loadType=result_list)

        # delete floor request
        if request.method == "DELETE":
            if newfloorindex > 0:
                newfloorindex -= 1
            return '', 200

        # Return base page.
        return render_template("newBase.html", project_id=project_id)

    @app.route("/opportunity/<int:project_id>/newalt",methods=['GET','PUT','POST'])
    def addAlt(project_id):
        if request.method == 'PUT':
            print(request.form)
            db = sqlite3.connect("loadBuilder.sqlite3")
            query = db.execute("SELECT ID, baseName FROM Bases Where projectID==?;", (int(project_id),))
            result_list = getfrom_db_as_dict_list(query)
            return render_template("altNew/selectBase.html",project_id=project_id, baseOptions=result_list)

        if request.method == 'POST':
            data = request.form.to_dict(flat=False)
            load_data_list = [tuple(map(int,floor.split(':'))) for floor in data["load"]]
            newAlt(project_id, data["name"][0],load_data_list)

        return render_template("newAlt.html", project_id=project_id)

    @app.route("/opportunity/<int:project_id>/newalt/getbase",methods=['PUT'])
    def getBaseOptions(project_id):
        db = sqlite3.connect("loadBuilder.sqlite3")
        query = db.execute("SELECT ID, floorNumber FROM Floors Where baseID==?;", (int(request.form["selected"]),))
        result_list = getfrom_db_as_dict_list(query)
        for floor in result_list:
            loads = query.execute("SELECT LoadTypes.ID, LoadTypes.loadName FROM FloorLoads INNER JOIN LoadTypes ON FloorLoads.loadType = LoadTypes.ID WHERE FloorLoads.ID==?;", (floor.get("ID"),))
            loads = getfrom_db_as_dict_list(loads)

            floor.update({"loads" : loads})

        return render_template("altNew/floorForm.html", floors=result_list, base_id=int(request.form["selected"]))

    @app.route("/opportunity/<int:project_id>/price",methods=['GET','POST'])
    def price(project_id):
        if request.method == 'POST':
            # accept new pricing data here
            pass
            return ''

        query = db.execute("select id, basename from bases where projectid==?;", (int(project_id),))
        result_list = getfrom_db_as_dict_list(query)
        return render_template("pricing.html",opportunity=project_id, unpricedBases=result_list)


    @app.route("/opportunity/<int:project_id>/price/getbase/<int:base_id>",methods=['PUT'])
    def getbaseforprice(project_id, base_id):
        db = sqlite3.connect("loadBuilder.sqlite3")
        query = db.execute("SELECT ID, baseName FROM Bases Where ID==?;", (int(base_id),))
        result_list = getfrom_db_as_dict_list(query)

        db = sqlite3.connect("loadBuilder.sqlite3")
        query = db.execute("SELECT altID, altName, price FROM BaseAlts join Alts ON Alts.ID == BaseAlts.altID Where baseID==?;", (int(base_id),))
        alts = getfrom_db_as_dict_list(query)
        return render_template("pricing/basePriceEstimation.html",base=result_list[0],alts=alts)

    return app

