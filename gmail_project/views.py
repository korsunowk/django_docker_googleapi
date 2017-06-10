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
import time

start_time = time.time()

flow = client.OAuth2WebServerFlow(client_id='890978714352-nnv2maasf1om2tnrttl25s3hdrgq9p4s.apps.googleusercontent.com',
                                  client_secret='sKjNKJRTw7Nt7TFw3ZIyyOJp',
                                  scope=['https://www.googleapis.com/auth/drive',
                                         'https://mail.google.com/',
                                         'https://www.googleapis.com/auth/drive.appdata',
                                         'https://www.googleapis.com/auth/drive.file',
                                         'https://www.googleapis.com/auth/drive.metadata',
                                         'https://www.googleapis.com/auth/drive.metadata.readonly',
                                         'https://www.googleapis.com/auth/drive.photos.readonly',
                                         'https://www.googleapis.com/auth/drive.readonly',
                                         'https://www.googleapis.com/auth/plus.me'],
                                  redirect_uri='http://127.0.0.1:8000/oauth2callback/')


def main(request):
    if request.user.is_authenticated():
        return render_to_response('email.html', get_all_emails)
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


def parse_message(request_id, response, exception):
    to_message, from_message, subject_message, message_body, date_message = '', '', '', '', ''
    global all_data
    for result_mess in response['payload']['headers']:
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


def parse_file(request_id, response, exeption):
    # print(request_id, response, exeption)
    print('_____________________________________________________________')


@login_required
def get_all_emails(request):
    credential = CredentialsModel.objects.get(
        id=request.user
    ).credential
    http = credential.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)

    all_data = dict()
    global all_data
    all_data['user_info'] = request.user.username
    all_data['messages'] = []

    messages = service.users().messages().list(userId='me', maxResults=100).execute()

    batch = service.new_batch_http_request()
    for message in messages['messages']:
        batch.add(service.users().messages().get(userId='me', 
                                                 id=message['id']), 
                  callback=parse_message)
    batch.execute(http=http)

    return JsonResponse(all_data)


@login_required
def get_all_files(request):
    credential = CredentialsModel.objects.get(
        id=request.user
    ).credential
    http = credential.authorize(httplib2.Http())
    service = discovery.build('drive', 'v2', http=http)

    files = service.files().list().execute()

    return JsonResponse(files, safe=False)
