from django.contrib.auth.models import auth
from django.http import JsonResponse

import json

from rest_framework import status

from datetime import datetime, timedelta

from book_service.models import Login
from book_service.model.UserModel import User
from book_service.model.LoginHistoryModel import LoginHistory
from book_service.model.TokenModel import Token

from book_service.helpers import (
    make_hash,
    generate_token,
    verify_token,
    response,
    validate
)


def login(request):
    # if request.user.is_authenticated:
    #     return JsonResponse(response(data='Already logged In', status_code=304))

    if request.method == 'POST':
        data = json.loads(request.body)
        fields = {
            "username": {
                "type": "string",
                "required": True
            },
            "password": {
                "type": "string",
                "required": True
            }
        }
        validation = validate(fields, data)
        if validation:
            return JsonResponse(response(data=validation, status_code=status.HTTP_400_BAD_REQUEST))

        check = Login.objects.filter(username=data['username']).first()
        if not check:
            return JsonResponse(response(data='Username not found', status_code=status.HTTP_404_NOT_FOUND))

        login = auth.authenticate(username=data['username'], password=data['password'])
        if not login:
            return JsonResponse(response(data='Wrong password', status_code=status.HTTP_400_BAD_REQUEST))

        auth.login(request, login)

        LoginHistory(
            login_id=login.id,
            login_at=datetime.now(),
        ).save()
        data = {
            'id':login.id,
            'username':login.username,
            'role':login.role,
            'expire':str(datetime.now() + timedelta(days=7))
        }
        token = generate_token(data)
        Token.objects.update_or_create(login_id=login.id, defaults={'token': token})

        response_with_token = JsonResponse(response(
            data = {'Token':token, 'Message':'Login Success'},
            status_code=status.HTTP_202_ACCEPTED,
            )
        )
        response_with_token.set_cookie('token', token)
        return response_with_token

    return JsonResponse(response(data='Method not allowed', status_code=status.HTTP_405_METHOD_NOT_ALLOWED))

def register(request):
    if request.user.is_authenticated:
        return JsonResponse(response(data='Already logged In', status_code=304))

    if request.method == 'POST':
        data = json.loads(request.body)
        fields = {
            "first_name": {
                "type": "string",
                "required": True
            },
            "last_name": {
                "type": "string",
                "nullable": True
            },
            "gender": {
                "type": "string",
                "allowed": ['male', 'female', 'other'],
                "required": True
            },
            "email": {
                "type": "string",
                "regex": '^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$',
                "required": True
            },
            "password": {
                "type": "string",
                "required": True
            },
            "confirm_password": {
                "type": "string",
                "required": True
            },
            "phone_number": {
                "type": "string",
                "required": True
            },
            "permanent_address": {
                "type": "string",
                "nullable": True
            },
            "temporary_address": {
                "type": "string",
                "required": True
            },
            "pincode": {
                "type": "string",
                "required": True
            },
        }
        validation = validate(fields, data)
        if validation:
            return JsonResponse(response(data=validation, status_code=status.HTTP_400_BAD_REQUEST))

        login = Login.objects.filter(username=data['email']).first()
        if login:
            return JsonResponse(response(data='Username or Email ID is already exists', status_code=status.HTTP_409_CONFLICT))

        if data['password'] != data['confirm_password']:
            return JsonResponse(response(data='Password Mismatch', status_code=status.HTTP_400_BAD_REQUEST))

        user = User.objects.filter(phone_number=data['phone_number']).first()
        if user:
            return JsonResponse(response(data='Phone number is already exists', status_code=status.HTTP_409_CONFLICT))

        new_login = Login(
            username=data['email'],
            password=make_hash(data['password']),
            role='user',
            active=True,
        )
        new_login.save()
        GENDER = ['male', 'female', 'other']
        if data['gender'].lower() not in GENDER:
            return JsonResponse(response(data='Gender value is not valid', status_code=status.HTTP_400_BAD_REQUEST))

        User(
            login_id=new_login.id,
            first_name=data['first_name'],
            last_name=data['last_name'] if 'lastname' in data else None,
            gender=data['gender'],
            phone_number=data['phone_number'],
            email=data['email'],
            permanent_address=data['permanent_address'] if 'permanent_address' in data else None,
            temporary_address=data['temporary_address'],
            pincode=data['pincode'],
        ).save()
        return JsonResponse(response(data='Successfully Registered', status_code=status.HTTP_201_CREATED))

    return JsonResponse(response(data='Method not allowed', status_code=status.HTTP_400_BAD_REQUEST))

def get_profile(request):
    if not request.COOKIES['token']:
        return JsonResponse(response(data='Auth Token not found', status_code=status.HTTP_401_UNAUTHORIZED))

    if request.method == 'GET':
        user = verify_token(request.COOKIES['token'])
        user = User.objects.filter(login_id=user['id']).first()
        if not user:
            return JsonResponse(response(data='Forbidden'), status_code=status.HTTP_403_FORBIDDEN)

        user_data = {
            'login_id' : user.login_id,
            'first_name' : user.first_name,
            'last_name' : user.last_name,
            'gender' : user.gender,
            'phone_number' : user.phone_number,
            'email' : user.email,
            'permanent_address' : user.permanent_address,
            'temporary_address' : user.temporary_address,
            'pincode' : user.pincode,
            'created_at' : user.created_at,
            'updated_at' : user.updated_at,
        }
        return JsonResponse(response(data=user_data, status_code=status.HTTP_200_OK))
    return JsonResponse(response(data='Method not allowed', status_code=status.HTTP_405_METHOD_NOT_ALLOWED))

def update_profile(request):
    if not request.COOKIES['token']:
        return JsonResponse(response(data='Auth Token not found', status_code=status.HTTP_401_UNAUTHORIZED))

    if request.method == 'PUT':
        user = verify_token(request.COOKIES['token'])
        user = User.objects.filter(login_id=user['id']).first()
        if not user:
            return JsonResponse(response(data='Forbidden'), status_code=status.HTTP_403_FORBIDDEN)

        data = json.loads(request.body)

        user.first_name = data['first_name'] if 'first_name' in data else user.first_name
        user.last_name = data['last_name'] if 'last_name' in data else user.last_name
        user.gender = data['gender'] if 'gender' in data else user.gender
        user.phone_number = data['phone_number'] if 'phone_number' in data else user.phone_number
        user.permanent_address = data['permanent_address'] if 'permanent_address' in data else user.permanent_address
        user.temporary_address = data['temporary_address'] if 'temporary_address' in data else user.temporary_address
        user.pincode = data['pincode'] if 'pincode' in data else user.pincode
        user.updated_at = datetime.now()

        user.save()
        user_data = {
            'login_id' : user.login_id,
            'first_name' : user.first_name,
            'last_name' : user.last_name,
            'gender' : user.gender,
            'phone_number' : user.phone_number,
            'email' : user.email,
            'permanent_address' : user.permanent_address,
            'temporary_address' : user.temporary_address,
            'pincode' : user.pincode,
            'created_at' : user.created_at,
            'updated_at' : user.updated_at,
        }
        return JsonResponse(response(data={'message':'Updated successfully', 'values':user_data}, status_code=status.HTTP_200_OK))
    return JsonResponse(response(data='Method not allowed', status_code=status.HTTP_405_METHOD_NOT_ALLOWED))

def reset_password(request):
    if not request.COOKIES['token']:
        return JsonResponse(response(data='Auth Token not found', status_code=status.HTTP_401_UNAUTHORIZED))

    if request.method == 'PUT':
        token_data = verify_token(request.COOKIES['token'])
        if not token_data:
            return JsonResponse(response(data='Forbidden'), status_code=status.HTTP_403_FORBIDDEN)

        data = json.loads(request.body)
        fields = {
            "new_password": {
                "type": "string",
                "required": True
            },
            "confirm_password": {
                "type": "string",
                "required": True
            }
        }
        validation = validate(fields, data)
        if validation:
            return JsonResponse(response(data=validation, status_code=status.HTTP_400_BAD_REQUEST))

        if data['new_password'] != data['confirm_password']:
            return JsonResponse(response(data='Password Mismatch', status_code=status.HTTP_400_BAD_REQUEST))

        Login.objects.filter(id=token_data['id']).update(password=make_hash(data['new_password']))
        return JsonResponse(response(data='Password Updated successfully', status_code=status.HTTP_200_OK))
    return JsonResponse(response(data='Method not allowed', status_code=status.HTTP_405_METHOD_NOT_ALLOWED))

def delete_account(request):
    if not request.COOKIES['token']:
        return JsonResponse(response(data='Auth Token not found', status_code=status.HTTP_401_UNAUTHORIZED))

    if request.method == 'DELETE':
        user = verify_token(request.COOKIES['token'])
        User.objects.filter(login_id=user['id']).delete()
        return logout(request)
    return JsonResponse(response(data='Method not allowed', status_code=status.HTTP_405_METHOD_NOT_ALLOWED))

def logout(request):
    if not request.COOKIES['token']:
        return JsonResponse(response(data='Already Logged out', status_code=status.HTTP_304_NOT_MODIFIED))

    if request.method == 'DELETE':
        auth.logout(request)
        response_with_token = JsonResponse(response(data='Logged out success', status_code=status.HTTP_200_OK))
        response_with_token.delete_cookie('token')
        return response_with_token
    return JsonResponse(response(data='Method not allowed', status_code=status.HTTP_405_METHOD_NOT_ALLOWED))
