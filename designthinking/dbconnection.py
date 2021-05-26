import ibm_db
import ibm_db_dbi

conn_str='DATABASE=BLUDB;HOSTNAME=dashdb-txn-sbox-yp-dal09-10.services.dal.bluemix.net;PORT=50001;PROTOCOL=TCPIP;UID=xrg65936;PWD=h057ldff0hhkb9@6;Security=SSL;'

ibm_db_conn = ibm_db.connect(conn_str,'','')
conn = ibm_db_dbi.Connection(ibm_db_conn)


def insertSingleTwo(tableName, value):
    insert = "insert into "+tableName+" values(?,?)"
    params = (value[0], value[1])
    stmt = ibm_db.prepare(ibm_db_conn, insert)
    ibm_db.execute(stmt, params)

def insertSingleFour(tableName, value):
    insert = "insert into "+tableName+" values(?,?,?,?)"
    params = (value[0], value[1], value[2], value[3])
    stmt = ibm_db.prepare(ibm_db_conn, insert)
    ibm_db.execute(stmt, params)


def insertTwo(projectID, tableName, context):
    insert = "insert into "+tableName+" values(?,?)"
    for element in context:
        params = (projectID, element)
        stmt = ibm_db.prepare(ibm_db_conn, insert)
        ibm_db.execute(stmt, params)


# save the user's input from new design to the database
def saveProject(email, context):
    projectID = context['id']
    insert = "insert into Project values(?,?)"
    params = (email, projectID)
    stmt = ibm_db.prepare(ibm_db_conn, insert)
    ibm_db.execute(stmt, params)

    insert = "insert into Target values(?,?)"
    params = (projectID, context['user'])
    stmt = ibm_db.prepare(ibm_db_conn, insert)
    ibm_db.execute(stmt, params)

    insert = "insert into ProjectName values(?,?)"
    params = (projectID, context['project_name'])
    stmt = ibm_db.prepare(ibm_db_conn, insert)
    ibm_db.execute(stmt, params)

    insertTwo(projectID, "EmpathyThink", context['empathy_think'])
    insertTwo(projectID, "EmpathyFeel", context['empathy_feel'])
    insertTwo(projectID, "EmpathySay", context['empathy_say'])
    insertTwo(projectID, "EmpathyDo", context['empathy_do'])

    insert = "insert into AsIs values(?,?,?)"
    for element in context['as_is']:
        params = (projectID, element['order'], element['text'])
        stmt = ibm_db.prepare(ibm_db_conn, insert)
        ibm_db.execute(stmt, params)


    insert = "insert into Ideas values(?,?,?,?)"
    for element in context['new_ideas']:
        params = (projectID, element['complexity'], element['expensive'],element['text'])
        stmt = ibm_db.prepare(ibm_db_conn, insert)
        ibm_db.execute(stmt, params)

def getData(tableName, colName, id):
    select = "select "+ colName+" from "+tableName+" where id = \'" + id +"\'"
    cur = conn.cursor()
    cur.execute(select)
    rows=cur.fetchall()
    return rows

def getProjectID(email): 
    id = []
    select = "select email, id from project where email = \'" + email +"\'"
    cur = conn.cursor()
    cur.execute(select)
    rows=cur.fetchall()
    if rows!=False:
        for row in rows:
            id.append(row[1])
    return id

def getProjectName(projectID):
    name = []
    for id in projectID:
        select = "select id, name from projectname where id = \'" + id +"\'"
        stmt_select = ibm_db.exec_immediate(ibm_db_conn, select)
        cols = ibm_db.fetch_tuple( stmt_select )
        if cols!=False:
            project = {'id': cols[0], 'name': cols[1]}
        select = "select id, target from target where id = \'" + id +"\'"
        stmt_select = ibm_db.exec_immediate(ibm_db_conn, select)
        cols = ibm_db.fetch_tuple( stmt_select )
        if cols!=False:
            project['user'] = cols[1]
        name.append(project)
    return name

def getProjectContent(projectID):
    content = {}
    params = [
        ['ProjectName', "name"],
        ['Target', 'target'],
        ['EmpathyThink', 'think'],
        ['EmpathyFeel', 'feel'],
        ['EmpathySay', 'say'],
        ['EmpathyDo', 'do'],
    ]
    for param in params:
        rows = getData(param[0], param[1], projectID)
        content[param[0]] = []
        for i in range(len(rows)):
            content[param[0]].append({'id': projectID, param[1]: rows[i][0], 'sequence': str(i)})
    param = ['AsIs', 'order, text']
    rows = getData(param[0], param[1], projectID)
    content[param[0]] = []
    for i in range(len(rows)):
        content[param[0]].append({'id': projectID, 'order': rows[i][0], 'text': rows[i][1], 'sequence': str(i)})
    param = ['Ideas', 'complexity, expensive, text']
    rows = getData(param[0], param[1], projectID)
    content[param[0]] = []
    for i in range(len(rows)):
        content[param[0]].append({'id': projectID, 'complexity': rows[i][0], 'expensive': rows[i][1], 'text': rows[i][2], 'sequence': str(i)})
    return content

def deleteProject(email, projectID):
    tables = ['asis', 'empathydo', 'empathyfeel', 'empathysay', 'empathythink', 'ideas', 'projectname', 'target']
    for table in tables:
        delete = "delete from "+table+" where id = \'" + projectID+ "\'"
        result = ibm_db.exec_immediate(ibm_db_conn,delete)
        print(result)
    delete = "delete from project where id = \'"+projectID+'\''
    result = ibm_db.exec_immediate(ibm_db_conn,delete)

def deleteItem(table, item):
    condition = "id =\'"
    condition = condition + item['id'] +'\''
    for key, value in item.items():
        if key!="id" and key!="sequence" and key!="complexity" and key!="expensive":
            condition = condition + " and " + key + " = \'" + value + '\''
    delete =  "delete from "+table+" where " + condition
    print(delete)
    result = ibm_db.exec_immediate(ibm_db_conn,delete)
    print(result)