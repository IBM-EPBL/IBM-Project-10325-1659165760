import os
import ibm_db

from flask            import Flask
from flask_login      import LoginManager
from flask_bcrypt     import Bcrypt

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

app.config.from_object('app.config.Config')

bc = Bcrypt      (app)

lm = LoginManager(   )
lm.init_app(app)


# DB
# DSN configurations
hostname = os.environ["DB_HOST"]
uid = os.environ["DB_USER"]
passwd = os.environ["DB_PASSWD"]
driver = "{IBM DB2 ODBC DRIVER}"
dbName = "BLUDB"
dbPort = os.environ["DB_PORT"]
proto = "TCPIP"
security = "SSL"

connOption = {ibm_db.SQL_ATTR_AUTOCOMMIT: ibm_db.SQL_AUTOCOMMIT_ON}

dsn = (
    "DRIVER={0};"
    "DATABASE={1};"
    "HOSTNAME={2};"
    "PORT={3};"
    "PROTOCOL={4};"
    "UID={5};"
    "PWD={6};"
    "SECURITY={7};").format(driver, dbName, hostname, dbPort, proto, uid, passwd, security)

# check connection
try:
    db = ibm_db.connect(dsn, '', '', connOption)
    server = ibm_db.server_info(db)
    print("[*] Connected DB Name: ", server.DB_NAME)
except Exception:
    print("[!X!] Unable to connect: ", ibm_db.conn_errormsg())
    exit(0)


# Import routing, models and Start the App
from app import views, models
