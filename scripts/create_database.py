import logging
import os
import sys
import sqlalchemy_utils


sys.path.append("../app")


url = os.environ.get("DATABASE_URL")
debug = os.environ.get("DEBUG")


if not sqlalchemy_utils.database_exists(url):
    sqlalchemy_utils.create_database(url)

    if debug == "True" or debug is None:
        print("Creating Database...")
    else:
        logging.info("Creating Database...")
else:
    if debug == "True" or debug is None:
        print("Database already exist...")
    else:
        logging.info("Database already exist...")
