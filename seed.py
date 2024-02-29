import os
from models import UserModel

admin = UserModel(password=os.environ.get('ADMIN_CODE'), username=os.environ.get('USER_NAME'), email=os.environ.get('EMAIL'), role=os.environ.get('ROLE'), verified=os.environ.get('VERIFIED'))