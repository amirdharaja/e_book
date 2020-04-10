from django.contrib.auth.models import auth
from django.http import JsonResponse

import json

from rest_framework import status

from datetime import datetime, timedelta

from book_service.model.UserModel import User
from book_service.model.BookModel import Book
from book_service.model.FavoriteBookModel import FavoriteBook
from book_service.model.CartModel import Cart

from book_service.helpers import (
    make_hash,
    generate_token,
    verify_token,
    response,
    validate,
    paginnations
)


def get_book(request):
    if not request.COOKIES['token']:
        return JsonResponse(response(data='Auth Token not found', status_code=status.HTTP_401_UNAUTHORIZED))

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

        book = Book.objects.filter(id=data['book_id']).first()
        if not book:
            return JsonResponse(response(data='Book not found', status_code=status.HTTP_404_NOT_FOUND))

        user = User.objects.filter(login_id=book.author_id).first()
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

def list_all_books(request):
    if not request.COOKIES['token']:
        return JsonResponse(response(data='Auth Token not found', status_code=status.HTTP_401_UNAUTHORIZED))

    if request.method == 'GET':
        books = Book.objects.order_by('-created_at')
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
        return JsonResponse(response(data=books_datas, meta=paginate_data[0], status_code=status.HTTP_200_OK))
    return JsonResponse(response(data='Method not allowed', status_code=status.HTTP_405_METHOD_NOT_ALLOWED))

def add_favourite_book(request):
    if not request.COOKIES['token']:
        return JsonResponse(response(data='Auth Token not found', status_code=status.HTTP_401_UNAUTHORIZED))

    if request.method == 'POST':
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

        check = FavoriteBook.objects.filter(book_id=data['book_id'], login_id=request.user.id).first()
        if check:
            return JsonResponse(response(data={'message':'Book already in favourite list'}, status_code=status.HTTP_304_NOT_MODIFIED))

        FavoriteBook(book_id=data['book_id'], login_id=request.user.id).save()
    
        return JsonResponse(response(data={'message':'New book successfully added into favourite list'}, status_code=status.HTTP_201_CREATED))
    return JsonResponse(response(data='Method not allowed', status_code=status.HTTP_405_METHOD_NOT_ALLOWED))

def remove_favourite_book(request):
    if not request.COOKIES['token']:
        return JsonResponse(response(data='Auth Token not found', status_code=status.HTTP_401_UNAUTHORIZED))

    if request.method == 'DELETE':
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

        check = FavoriteBook.objects.filter(book_id=data['book_id'], login_id=request.user.id).first()
        if not check:
            return JsonResponse(response(data={'message':'Book not found to remove'}, status_code=status.HTTP_404_NOT_FOUND))

        check.delete()
        return JsonResponse(response(data={'message':'Book successfully removed from the favourite list'}, status_code=status.HTTP_200_OK))
    return JsonResponse(response(data='Method not allowed', status_code=status.HTTP_405_METHOD_NOT_ALLOWED))

def remove_all_favourite_books(request):
    if not request.COOKIES['token']:
        return JsonResponse(response(data='Auth Token not found', status_code=status.HTTP_401_UNAUTHORIZED))

    if request.method == 'DELETE':
        FavoriteBook.objects.filter(login_id=request.user.id).delete()
        return JsonResponse(response(data={'message':'All books successfully removed from the favourite list'}, status_code=status.HTTP_200_OK))

    return JsonResponse(response(data='Method not allowed', status_code=status.HTTP_405_METHOD_NOT_ALLOWED))

def list_all_favourite_books(request):
    if not request.COOKIES['token']:
        return JsonResponse(response(data='Auth Token not found', status_code=status.HTTP_401_UNAUTHORIZED))

    if request.method == 'GET':
        book_ids = FavoriteBook.objects.filter(login_id=request.user.id).values_list('book_id', flat=True)
        books = Book.objects.filter(id__in=book_ids).order_by('-created_at')
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
        return JsonResponse(response(data=books_datas, meta=paginate_data[0], status_code=status.HTTP_200_OK))
    return JsonResponse(response(data='Method not allowed', status_code=status.HTTP_405_METHOD_NOT_ALLOWED))

def add_cart(request):
    if not request.COOKIES['token']:
        return JsonResponse(response(data='Auth Token not found', status_code=status.HTTP_401_UNAUTHORIZED))

    if request.method == 'POST':
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

        check = Cart.objects.filter(book_id=data['book_id'], login_id=request.user.id).first()
        if check:
            return JsonResponse(response(data={'message':'Book already in Cart'}, status_code=status.HTTP_304_NOT_MODIFIED))

        Cart(book_id=data['book_id'], login_id=request.user.id).save()
    
        return JsonResponse(response(data={'message':'New book successfully added into your Cart'}, status_code=status.HTTP_201_CREATED))
    return JsonResponse(response(data='Method not allowed', status_code=status.HTTP_405_METHOD_NOT_ALLOWED))

def remove_cart(request):
    if not request.COOKIES['token']:
        return JsonResponse(response(data='Auth Token not found', status_code=status.HTTP_401_UNAUTHORIZED))

    if request.method == 'DELETE':
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

        check = Cart.objects.filter(book_id=data['book_id'], login_id=request.user.id).first()
        if not check:
            return JsonResponse(response(data={'message':'Book not found to remove'}, status_code=status.HTTP_404_NOT_FOUND))

        check.delete()
        return JsonResponse(response(data={'message':'Book successfully removed from your Cart'}, status_code=status.HTTP_200_OK))
    return JsonResponse(response(data='Method not allowed', status_code=status.HTTP_405_METHOD_NOT_ALLOWED))

def remove_all_carts(request):
    if not request.COOKIES['token']:
        return JsonResponse(response(data='Auth Token not found', status_code=status.HTTP_401_UNAUTHORIZED))

    if request.method == 'DELETE':
        Cart.objects.filter(login_id=request.user.id).delete()
        return JsonResponse(response(data={'message':'All books successfully removed from your Cart'}, status_code=status.HTTP_200_OK))

    return JsonResponse(response(data='Method not allowed', status_code=status.HTTP_405_METHOD_NOT_ALLOWED))

def list_all_carts(request):
    if not request.COOKIES['token']:
        return JsonResponse(response(data='Auth Token not found', status_code=status.HTTP_401_UNAUTHORIZED))

    if request.method == 'GET':
        book_ids = Cart.objects.filter(login_id=request.user.id).values_list('book_id', flat=True)
        books = Book.objects.filter(id__in=book_ids).order_by('-created_at')
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
        return JsonResponse(response(data=books_datas, meta=paginate_data[0], status_code=status.HTTP_200_OK))
    return JsonResponse(response(data='Method not allowed', status_code=status.HTTP_405_METHOD_NOT_ALLOWED))
