import ibm_db

from app         import db
from flask_login import UserMixin

class Users(UserMixin):
    def __init__(self, user, email, password):
        self.user       = user
        self.password   = password
        self.email      = email

    def save(self):
        # 1. Insert to DB
        sqlcmd = "INSERT INTO users(email, username,passwd) VALUES(?, ?, ?);"
        try:
            prepStmt = ibm_db.prepare(db, sqlcmd)
        except Exception:
            print("Error creating prep statmt!")
            exit(0)
        val = (self.email, self.user, self.password)
        ibm_db.bind_param(prepStmt, 1, val[0])
        ibm_db.bind_param(prepStmt, 2, val[1])
        ibm_db.bind_param(prepStmt, 3, val[2])
        ibm_db.execute(prepStmt)
        return self 

    def userExists(uname):
        sqlcmd = "SELECT username FROM users"

        try:
            res = ibm_db.exec_immediate(db, sqlcmd)
        except Exception:
            print("! Error executing SQL stmt")
            print(ibm_db.stmt_errormsg())
            exit(0)

        row = ibm_db.fetch_assoc(res)
        while row:
            if(row['USERNAME'] == uname):
                return True
            row = ibm_db.fetch_assoc(res)
        return False

    def emailExists(email):
        sqlcmd = "SELECT email FROM users"

        try:
            res = ibm_db.exec_immediate(db, sqlcmd)
        except Exception:
            print("! Error executing SQL stmt")
            print(ibm_db.stmt_errormsg())
            exit(0)

        row = ibm_db.fetch_assoc(res)
        while row:
            if(row['EMAIL'] == email):
                return True
            row = ibm_db.fetch_assoc(res)
        return False

    def getUser(uid):
        # RET: mail, uname, pass
        cmd = f"SELECT email, username, passwd FROM users WHERE uid={uid}"
        try:
            res = ibm_db.exec_immediate(db, cmd)
        except Exception:
            print("! Error executing SQL stmt")
            print(ibm_db.stmt_errormsg())
            exit(0)
        row = ibm_db.fetch_assoc(res)
        return row['EMAIL'], row['USERNAME'], row['PASSWD']
        
    def getUserWithUname(uname):
        # RET: mail, uname, pass
        cmd = f"SELECT email, username, passwd FROM users WHERE username='{uname}'"
        try:
            res = ibm_db.exec_immediate(db, cmd)
        except Exception:
            print("! Error executing SQL stmt")
            print(ibm_db.stmt_errormsg())
            exit(0)
        row = ibm_db.fetch_assoc(res)
        return row['EMAIL'], row['USERNAME'], row['PASSWD']

    def get_id(self):
        uname = self.user
        cmd = f"SELECT uid FROM users WHERE username='{uname}'"
        try:
            res = ibm_db.exec_immediate(db, cmd)
        except Exception:
            print("! Error executing SQL stmt")
            print(ibm_db.stmt_errormsg())
            exit(0)
        row = ibm_db.fetch_assoc(res)
        return row['UID']

    def getHistory(self):
        uid = self.get_id()
        cmd = f"SELECT results FROM history WHERE uid={uid}"
        print(cmd)
        try:
            res = ibm_db.exec_immediate(db, cmd)
        except Exception:
            print("Error fetching from history table.")
            exit(0)
        
        history = []
        row = ibm_db.fetch_assoc(res)
        while row:
            history += [row["RESULTS"]]
            row = ibm_db.fetch_assoc(res)
        return history


    def addHistory(self, currRes):
        uid = self.get_id()
        sqlcmd = "INSERT INTO history(uid, results) VALUES(?, ?);"
        try:
            prepStmt = ibm_db.prepare(db, sqlcmd)
        except Exception:
            print("Error creating prep statmt!")
            exit(0)
        ibm_db.bind_param(prepStmt, 1, uid)
        ibm_db.bind_param(prepStmt, 2, currRes)
        ibm_db.execute(prepStmt)
        if (ibm_db.num_rows(prepStmt) == 1):
            return True
        else:
            return False