import json
from django.http import JsonResponse
from rest_framework import status

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from book_service.models import Login
from book_service.model.UserModel import User
from book_service.model.BookModel import Book

from book_service.helpers import (
    verify_token,
    response,
    validate,
    verify_token_with_role,
    paginnations
)

def get_my_book(request):
    if not request.COOKIES['token']:
        return JsonResponse(response(data='Auth Token not found', status_code=status.HTTP_401_UNAUTHORIZED))

    path = str(request.path).split('/')
    user = verify_token_with_role(request.COOKIES['token'], path[1])
    if not user:
        return JsonResponse(response(data='Unauthorized, You dont have privilege to access this page', status_code=status.HTTP_401_UNAUTHORIZED))

    if request.method == 'GET':
        data = json.loads(request.body)
        fields = {
            "book_id": {
                "type": "integer",
                "required": True
            },
        }
        validation = validate(fields, data)

        if validation:
            return JsonResponse(response(data=validation, status_code=status.HTTP_400_BAD_REQUEST))

        book = Book.objects.filter(id=data['book_id'], author_id=request.user.id).first()
        if not book:
            return JsonResponse(response(data='Book not found', status_code=status.HTTP_404_NOT_FOUND))

        user = User.objects.filter(login_id=request.user.id).first()
        book_data = {
            'title' : book.title,
            'amazon_url' : book.amazon_url,
            'genre(type)' : book.genre,
            'created_at' : book.created_at,
            'updated_at' : book.updated_at,
            'author_id' : book.author_id,
            'author_details' : {
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
        }
        return JsonResponse(response(data=book_data, status_code=status.HTTP_200_OK))
    return JsonResponse(response(data='Method not allowed', status_code=status.HTTP_405_METHOD_NOT_ALLOWED))

def list_my_books(request):
    if not request.COOKIES['token']:
        return JsonResponse(response(data='Auth Token not found', status_code=status.HTTP_401_UNAUTHORIZED))

    path = str(request.path).split('/')
    user = verify_token_with_role(request.COOKIES['token'], path[1])
    if not user:
        return JsonResponse(response(data='Unauthorized, You dont have privilege to access this page', status_code=status.HTTP_401_UNAUTHORIZED))

    if request.method == 'GET':
        books = Book.objects.filter(author_id=request.user.id)
        if not books:
            return JsonResponse(response(data='Books not found', status_code=status.HTTP_404_NOT_FOUND))

        page = request.GET.get('page') if request.GET.get('page') else "1"
        paginate_data = paginnations(books, page, request.path)
        if not paginate_data:
            return JsonResponse(response(data='Books not found for page={}'.format(request.GET.get('page')), status_code=status.HTTP_404_NOT_FOUND))

        books_datas = []
        for book in paginate_data[1]:
            data = {
                'book_id' : book.id,
                'title' : book.title,
                'amazon_url' : book.amazon_url,
                'genre(type)' : book.genre,
                'created_at' : book.created_at,
                'updated_at' : book.updated_at,
                'author_id' : book.author_id,
            }
            books_datas.append(data)
        user = User.objects.filter(login_id=request.user.id).first()
        return JsonResponse(response(data=books_datas, meta=paginate_data[0], status_code=status.HTTP_200_OK))
    return JsonResponse(response(data='Method not allowed', status_code=status.HTTP_405_METHOD_NOT_ALLOWED))

def add_new_book(request):
    if not request.COOKIES['token']:
        return JsonResponse(response(data='Auth Token not found', status_code=status.HTTP_401_UNAUTHORIZED))

    path = str(request.path).split('/')
    user = verify_token_with_role(request.COOKIES['token'], path[1])
    if not user:
        return JsonResponse(response(data='Unauthorized, You dont have privilege to access this page', status_code=status.HTTP_401_UNAUTHORIZED))

    if request.method == 'POST':
        data = json.loads(request.body)
        fields = {
            "title": {
                "type": "string",
                "required": True
            },
            "amazon_url": {
                "type": "string",
                "required": True
            },
            "genre": {
                "type": "string",
                "required": True
            },
        }
        validation = validate(fields, data)

        if validation:
            return JsonResponse(response(data=validation, status_code=status.HTTP_400_BAD_REQUEST))

        book = Book(
            author_id=request.user.id,
            title=data['title'],
            amazon_url=data['amazon_url'],
            genre=data['genre'],
        )
        book.save()

        book_data = {
            'id' : book.id,
            'author_id' : book.author_id,
            'title' : book.title,
            'amazon_url' : book.amazon_url,
            'genre(type)' : book.genre,
            'created_at' : book.created_at,
        }
        return JsonResponse(response(data={'message':'New book added successfully','New_Book_Details':book_data}, status_code=status.HTTP_200_OK))
    return JsonResponse(response(data='Method not allowed', status_code=status.HTTP_405_METHOD_NOT_ALLOWED))

def delete_my_book(request):
    if not request.COOKIES['token']:
        return JsonResponse(response(data='Auth Token not found', status_code=status.HTTP_401_UNAUTHORIZED))

    path = str(request.path).split('/')
    user = verify_token_with_role(request.COOKIES['token'], path[1])
    if not user:
        return JsonResponse(response(data='Unauthorized, You dont have privilege to access this page', status_code=status.HTTP_401_UNAUTHORIZED))

    if request.method == 'DELETE':
        data = json.loads(request.body)
        fields = {
            "book_id": {
                "type": "integer",
                "required": True
            }
        }
        validation = validate(fields, data)

        if validation:
            return JsonResponse(response(data=validation, status_code=status.HTTP_400_BAD_REQUEST))

        check = Book.objects.filter(id=data['book_id']).first()

        if not check:
            return JsonResponse(response(data='Book not found', status_code=status.HTTP_404_NOT_FOUND))

        if check.author_id != request.user.id:
            return JsonResponse(response(data='This book author is not you, So you cant delete', status_code=status.HTTP_403_FORBIDDEN))

        check.delete()
        return JsonResponse(response(data='Book deleted', status_code=status.HTTP_200_OK))
    return JsonResponse(response(data='Method not allowed', status_code=status.HTTP_405_METHOD_NOT_ALLOWED))

def delete_my_books(request):
    if not request.COOKIES['token']:
        return JsonResponse(response(data='Auth Token not found', status_code=status.HTTP_401_UNAUTHORIZED))

    path = str(request.path).split('/')
    user = verify_token_with_role(request.COOKIES['token'], path[1])
    if not user:
        return JsonResponse(response(data='Unauthorized, You dont have privilege to access this page', status_code=status.HTTP_401_UNAUTHORIZED))

    if request.method == 'DELETE':

        Book.objects.filter(author_id=request.user.id).delete()

        return JsonResponse(response(data='All Books are deleted', status_code=status.HTTP_200_OK))
    return JsonResponse(response(data='Method not allowed', status_code=status.HTTP_405_METHOD_NOT_ALLOWED))
