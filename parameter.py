import os.path

from dotenv import load_dotenv

dotenv_path = "config.env"
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
user_postgresql = os.getenv("USER")
password_postgresql = os.getenv("PASSWORD")
localhost = os.getenv("HOST")
port_postgresql = os.getenv("PORT")
name_db = os.getenv("DB_NAME")
token = os.getenv("TOKEN")
