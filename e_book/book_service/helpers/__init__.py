from django.conf import settings
from django.contrib.auth.hashers import make_password

from datetime import datetime

from book_service.models import Login

import jwt
from jwt import DecodeError

import cerberus

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from rest_framework import status


SALT = settings.SALT
HASHER = settings.HASHER

JWT_SECRET_KEY = settings.JWT_SECRET_KEY
JWT_ALGORITHM = settings.JWT_ALGORITHM

def make_hash(user_password):
    hash_password = make_password(user_password, salt=SALT, hasher=HASHER)
    return hash_password

def generate_token(data):
    if data:
        token = jwt.encode(data, JWT_SECRET_KEY, JWT_ALGORITHM).decode('utf-8')
        return token

    return None

def verify_token(token):
    if token:
        try:
            data = jwt.decode(token, JWT_SECRET_KEY, JWT_ALGORITHM)
            expire_date = datetime.strptime(data['expire'], '%Y-%m-%d %H:%M:%S.%f')
            if datetime.now() >= expire_date:
                return None
            check_role = Login.objects.get(id=data['id'])
            if not check_role:
                return None
            if check_role.role == 'blocked_user':
                return None
            return data

        except jwt.DecodeError:
            return None

    return None

def verify_token_with_role(token, role):
    data = verify_token(token)
    if data:
        if data['role'] == role:
            return data
        return None


def response(data={}, meta={}, status_code=None):
    return {
        "data": data,
        "meta": meta,
        "status_code": status_code
    }

def validate(schema, data):
    input_validation = cerberus.Validator()
    if input_validation.validate(data, schema) == False:
        return input_validation.errors

def paginnations(datas, page, path):
    no_of_page_per_page = 10
    paginator = Paginator(datas, no_of_page_per_page)
    if int(page) <= 0 or int(page) > paginator.num_pages:
        return None
    try:
        datas = paginator.page(page)
    except PageNotAnInteger:
        datas = paginator.page(1)
    except EmptyPage:
        datas = paginator.page(paginator.num_pages)

    p = paginator.page(page)
    current_page = path+'?page='+ page,
    next_page = path+'?page='+ str(int(page)+1) if p.has_next() else None,
    previous_page = path+'?page='+ str(int(page)-1) if p.has_previous() else None,
    paginate_details = {
        'total_books':paginator.count,
        'total_pages':paginator.num_pages,
        'books_per_page': no_of_page_per_page,
        'current_page': current_page[0],
        'next_page':next_page[0],
        'previous_page':previous_page[0],
    }
    print(paginate_details,'-----------------------')
    return [paginate_details, datas]