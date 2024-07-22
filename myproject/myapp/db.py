from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password, check_password
from django.db import IntegrityError

User = get_user_model()

def create_database():
    # 데이터베이스는 Django가 관리하므로 특별한 작업이 필요 없습니다.
    pass

def register_user(username, email, password):
    try:
        user = User.objects.create(username=username, email=email, password=make_password(password))
        user.save()
        return True
    except IntegrityError:
        return False

def authenticate_user(username, password):
    try:
        user = User.objects.get(username=username)
        if check_password(password, user.password):
            return True
        else:
            return False
    except User.DoesNotExist:
        return False

def delete_user(username):
    try:
        user = User.objects.get(username=username)
        user.delete()
        return True
    except User.DoesNotExist:
        return False

def update_user(username, new_email=None, new_password=None):
    try:
        user = User.objects.get(username=username)
        if new_email:
            user.email = new_email
        if new_password:
            user.password = make_password(new_password)
        user.save()
        return True
    except User.DoesNotExist:
        return False

def find_user(username):
    try:
        user = User.objects.get(username=username)
        return user
    except User.DoesNotExist:
        return None
