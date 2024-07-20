from dotenv import load_dotenv
import os
load_dotenv()
TOKEN = os.environ.get("TOKEN")
SSL_CERTIFICATE = os.environ.get('SSL_CERTIFICATE')
SSL_CERTIFICATE_KEY = os.environ.get('SSL_CERTIFICATE_KEY')
SSL_DHPARAM = os.environ.get('SSL_DHPARAM')
