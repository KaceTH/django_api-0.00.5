from datetime import datetime, timedelta
from random import randint
from django.shortcuts import render

from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated

from rest_framework.response import Response
from rest_framework.views import APIView

from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie 
from rest_framework.parsers import JSONParser
from django.http import JsonResponse

from Authentication.utils import generate_access_token, generate_refresh_token

from django.contrib.auth import authenticate, login
from Authentication.models import User, Verification
from .serializer import CreateUser, ReadUser, CreateVerification

from verify_email.email_handler import send_verification_email
from django.core.mail import send_mail
from django.conf import settings

# Create your views here.

@csrf_exempt
@ensure_csrf_cookie
def login(request):
    if request.method == 'POST':
        data = JSONParser().parse(request)

        username = data['username']
        password = data['password']
        loginUser = authenticate(username=username, password=password)
        
        if loginUser is None:
            res = dict(
                code="00101",
                Message="User is not existed or password is worng",
                status=404
            )
            return JsonResponse(res, status=404)

        else :
            access_token = generate_access_token(loginUser)
            refresh_token = generate_refresh_token(loginUser)

            tokens = dict(
                access_token=access_token,
                refresh_token=refresh_token
            )
            res = dict(
                code="10101",
                Message="login Successed",
                status=200,
                info = tokens
            )
            return JsonResponse(res, safe=False)

    else :
        message = "You must send 'POST' request"
        return JsonResponse(dict(Message=f'{message}'), safe=False)


@csrf_exempt
def signIn(request):
    data = JSONParser().parse(request)

    if request.method == 'POST':
        try :
            User.objects.get(username=data['username'])
            return JsonResponse({"error" : 1}, status=400)
        except :
            pass

        try :
            User.objects.get(email=data['email'])
            return JsonResponse({"error" : 2}, status=400)
        except :
            pass

        try :
            User.objects.get(
                grade_number    = data['grade_number'],
                class_number    = data['class_number'],
                student_number  = data['student_number']
            )
            return JsonResponse({"error" : 3}, status=400)
        except :
            pass

        serializer = CreateUser(data=data)

        if serializer.is_valid():
            serializer.save()
            return JsonResponse({"pass" : 1}, safe=False)


@api_view()
@permission_classes((IsAuthenticated, ))
def user_setting(request, username):
    try:
        getUser = User.objects.get(username=username)
    except User.DoesNotExist:
        return JsonResponse({'error' : 1})

    res = {}
    if request.method == 'GET':
        serializer = ReadUser(getUser)
        res['info'] = serializer.data
        return JsonResponse(res, safe=False)
    
    if request.method == 'PUT':
        data = JSONParser().parse(request)
        return JsonResponse({"Message" : 3})
    
    elif request.method == 'DELETE':
        return JsonResponse({"Message" : 4})

    return JsonResponse("")

    
def register_user(request):
    inactive_user = send_verification_email(request)

@csrf_exempt
def email_verification(request, username):
    try:
        getUser = User.objects.get(username=username)
    except User.DoesNotExist:
        return JsonResponse({"E" : 1})

    if request.method == 'GET':
        if getUser.is_verificated == True :
            return JsonResponse({"error" : "already"})

        code = randint(123456,999999)

        try :
            getVerific = Verification.objects.get(author=getUser)
            getVerific.delete()
        except Verification.DoesNotExist:
            pass

        verification = Verification.objects.create(
            author=getUser,
            code=code,
        )
        verification.send_verification()
        verification.set_end_date()

        return JsonResponse({
            "pass" : 1,
            "info" : getUser.email
        })

    if request.method == 'POST':
        try :
            getVerific = Verification.objects.get(author=getUser)
        except Verification.DoesNotExist:
            return JsonResponse({
                "error" : 2
            })

        data = JSONParser().parse(request)
        if getVerific.is_end_date() == True:
            return JsonResponse({"error" : "due date"})

        if data['code'] == getVerific.code :
            getVerific.delete()
            getUser.is_verificated = True
            getUser.save()

            return JsonResponse({
                "pass" : 2
            })
        return JsonResponse({
            "error" : "wa",
        })


@csrf_exempt
def find_pw(request):
    if request.method == 'POST':
        data = JSONParser().parse(request)

        username = data['user_id']
        email = data['email']

        try :
            getUser = User.objects.get(username=username, email=email)
        except User.DoesNotExist:
            return JsonResponse({"error" : 1})
        
        message = f"your password is '{getUser.password}'"
        title = f"{getUser.username}'s password"

        send_mail(
            title,
            message,
            settings.EMAIL_HOST_USER,
            [getUser.email]
        )

        return JsonResponse({
            "message" : "password has sent to your email"
        })
    return JsonResponse({"M" : 1})
