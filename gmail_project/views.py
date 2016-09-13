from django.shortcuts import render_to_response, redirect, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from oauth2client import client
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
import httplib2
from apiclient import discovery
from django.contrib.auth.models import User
from gmail_project.models import CredentialsModel
from django.http import JsonResponse


flow = client.OAuth2WebServerFlow(client_id='890978714352-nnv2maasf1om2tnrttl25s3hdrgq9p4s.apps.googleusercontent.com',
                                  client_secret='sKjNKJRTw7Nt7TFw3ZIyyOJp',
                                  scope=['https://mail.google.com/', 'https://www.googleapis.com/auth/plus.me'],
                                  redirect_uri='http://127.0.0.1:8000/oauth2callback/')


def main(request):
    if request.user.is_authenticated():
        return render_to_response('email.html')
    else:
        return render_to_response('login.html')


@csrf_exempt
def index(request):
    auth_uri = flow.step1_get_authorize_url()
    return redirect(auth_uri)


@csrf_exempt
def logout_(request):
    logout(request)
    return render_to_response('login.html')


def auth_return(request):

    credential = flow.step2_exchange(request.GET['code'])
    http = credential.authorize(httplib2.Http())
    user_info_service = discovery.build(
        serviceName='oauth2', version='v2',
        http=http)
    user_info = user_info_service.userinfo().get().execute()

    user = User.objects.get_or_create(
        username=user_info['name'],
        password=''
    )
    try:
        credential_ = CredentialsModel.objects.get(
            id=user[0],
        )
        credential_.credential = credential
        credential_.save()
    except CredentialsModel.DoesNotExist:
        CredentialsModel.objects.create(
            id=user[0],
            credential=credential
        )

    login(request, user[0])

    return HttpResponseRedirect("/")


@login_required
def get_all_emails(request):
    credential = CredentialsModel.objects.get(
        id=request.user
    ).credential
    http = credential.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http, )

    all_data = dict()
    all_data['user_info'] = request.user.username
    all_data['messages'] = []
    to_message, from_message, subject_message, message_body, date_message = '', '', '', '', ''

    messages = service.users().messages().list(userId='me', maxResults=100).execute()

    for message in messages['messages']:
        result_message = service.users().messages().get(userId='me', id=message['id']).execute()
        message_body = result_message['snippet']
        for result_mess in result_message['payload']['headers']:
            if result_mess['name'] == 'Date':
                date_message = result_mess['value']
            elif result_mess['name'] == 'To':
                to_message = result_mess['value']
            elif result_mess['name'] == 'Subject':
                subject_message = result_mess['value']
            elif result_mess['name'] == 'From':
                from_message = result_mess['value']

        all_data['messages'].append(
            {
                'To': to_message,
                'From': from_message,
                'Date': date_message,
                'Subject': subject_message,
                'Message': message_body
            }
        )

    return JsonResponse(all_data)
