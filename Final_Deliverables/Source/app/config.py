import os
from   decouple import config

basedir = os.path.abspath(os.path.dirname(__file__))

class Config():

    CSRF_ENABLED = True
	
    # Set up the App SECRET_KEY
    SECRET_KEY = config('SECRET_KEY', default='S#perS3crEt_007')

    UPLOAD_FOLDER = "uploads"