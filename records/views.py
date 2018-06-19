''' View functions for authorization and integration of apps in YA '''

# -*- coding: utf-8 -*-


import json
import traceback
import urllib
import requests
from django.http import HttpResponse
from django.shortcuts import render
import uuid

from django.urls import reverse
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseServerError
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from yellowant import YellowAnt
from yellowant.messageformat import MessageClass, MessageAttachmentsClass, MessageButtonsClass


from records.commandcentre import CommandCentre
from records.models import YellowUserToken,YellowAntRedirectState, AppRedirectState, DropBoxUserToken

# Create your views here.



def redirectToYellowAntAuthenticationPage(request):
    print("In redirectToYellowAntAuthenticationPage")
    '''Initiate the creation of a new user integration on YA
       YA uses oauth2 as its authorization framework.
       This method requests for an oauth2 code from YA to start creating a
       new user integration for this application on YA.
    '''

    # Generate a unique ID to identify the user when YA returns an oauth2 code
    user = User.objects.get(id=request.user.id)
    state = str(uuid.uuid4())

    # Save the relation between user and state so that we can identify the user
    # when YA returns the oauth2 code
    YellowAntRedirectState.objects.create(user=user.id, state=state)

    # Redirect the application user to the YA authentication page.
    # Note that we are passing state, this app's client id,
    # oauth response type as code, and the url to return the oauth2 code at.
    return HttpResponseRedirect("{}?state={}&client_id={}&response_type=code&redirect_url={}".format
                                (settings.YELLOWANT_OAUTH_URL, state, settings.YELLOWANT_CLIENT_ID,
                                 settings.YELLOWANT_REDIRECT_URL))


def yellowantRedirecturl(request):
    print("In yellowantRedirecturl")

    ''' Receive the oauth2 code from YA to generate a new user integration
        This method calls utilizes the YA Python SDK to create a new user integration on YA.
        This method only provides the code for creating a new user integration on YA.
        Beyond that, you might need to authenticate the user on
        the actual application (whose APIs this application will be calling) and store a relation
        between these user auth details and the YA user integration.
    '''

    # Oauth2 code from YA, passed as GET params in the url
    code = request.GET.get('code')

    # The unique string to identify the user for which we will create an integration
    state = request.GET.get("state")

    # Fetch user with help of state from database
    yellowant_redirect_state = YellowAntRedirectState.objects.get(state=state)
    user = yellowant_redirect_state.user

    # Initialize the YA SDK client with your application credentials
    y = YellowAnt(app_key=settings.YELLOWANT_CLIENT_ID,
                  app_secret=settings.YELLOWANT_CLIENT_SECRET,
                  access_token=None, redirect_uri=settings.YELLOWANT_REDIRECT_URL)

    # Getting the acccess token
    access_token_dict = y.get_access_token(code)
    print(access_token_dict)

    access_token = access_token_dict['access_token']



    # Getting YA user details
    yellowant_user = YellowAnt(access_token=access_token)
    profile = yellowant_user.get_user_profile()

    # Creating a new user integration for the application
    user_integration = yellowant_user.create_user_integration()
    hash_str = str(uuid.uuid4()).replace("-", "")[:25]
    ut = YellowUserToken.objects.create(user=user, yellowant_token=access_token,
                                        yellowant_id=profile['id'],
                                        yellowant_integration_invoke_name=user_integration\
                                            ["user_invoke_name"],
                                        yellowant_integration_id=user_integration\
                                            ['user_application'],
                                        webhook_id=hash_str)

    state = str(uuid.uuid4())
    AppRedirectState.objects.create(user_integration=ut, state=state)

    url = "https://www.dropbox.com/oauth2/authorize/"
    params = { 'response_type': 'code','client_id': settings.DROPBOX_CLIENT_ID,
               'redirect_uri': settings.DROPBOX_REDIRECT_URL,
               'state': state}
    url += '?' + urllib.parse.urlencode(params)
    return HttpResponseRedirect(url)


def dropboxRedirecturl(request):
    # DropBoxUserToken.objects.create(user_integration=ut)
    ''' OAuth2 at Dropbox server '''
    if request.method == "GET":
        print("In dropboxRedirecturl GET")

        code = request.GET.get("code", False)
        print(code)

        state = request.GET.get("state")
        print(state)

        dropbox_redirect_state = AppRedirectState.objects.get(state=state)
        ut = dropbox_redirect_state.user_integration
        error = request.GET.get('error', None)
        print(error)

        # Checking status of auth request
        if error == 'access_denied':
            return HttpResponse('Access denied')
        if state is None:
            return HttpResponseBadRequest()

        # Getting auth code
        auth_code = request.GET.get('code', None)
        if auth_code is None:
            return HttpResponseBadRequest()

        print("------ Auth code here -----")
        print (auth_code)

        ## Getting access token

        url = "https://api.dropboxapi.com/oauth2/token/"
        headers = {'Accept': 'application/json', 'content-type': 'application/x-www-form-urlencoded'}
        params = {'code': code, 'grant_type': 'authorization_code','client_id': settings.DROPBOX_CLIENT_ID,
                  'client_secret' : settings.DROPBOX_CLIENT_SECRET,'redirect_uri': settings.DROPBOX_REDIRECT_URL
                  }

        print("In POST request")
        r = requests.post(url, data=params, headers=headers)
        if r.status_code != 200:
            return HttpResponse(r.text)

        access_token_dict = json.loads(r.text)
        uid = access_token_dict['uid']
        accessToken = access_token_dict['access_token']
        account_id = access_token_dict['account_id']
        token_type = access_token_dict['token_type']

        DropBoxUserToken.objects.create(user_integration=ut,accessToken=accessToken,account_id=account_id)
        print(access_token_dict)
        return HttpResponseRedirect("/")

# @csrf_exempt
# def webhook(request, hash_str=""):
#     print("Inside webhook")
#     code = request.GET.get("code", False)
#
#     if code == request.codes.ok:
#         data =  (request.body.decode('utf-8'))
#         response_json = json.loads(data)
#         print(response_json)
#
#         try:
#             operation = response_json['eventNotifications'][0]['dataChangeEvent']['entities'][0]['operation']
#             name = response_json['eventNotifications'][0]['dataChangeEvent']['entities'][0]['name']
#         except:
#             pass
#
#         print(operation)
#
#         if operation == 'Create':
#             if name == 'Customer':
#                 add_new_customer(request,hash_str)
#             else:
#                 add_new_invoice(request,hash_str)
#         else:
#             update_invoice(request,hash_str)
#
#         return HttpResponse('OK',status=200)
#     else:
#         return HttpResponse(status=400)
#
# def update_invoice(request,webhook_id):
#
#     """
#     Webhook function to notify user about newly created invoice
#     """
#     print("In update_invoice")
#
#     # Extracting necessary data
#     code = request.GET.get("code", False)
#
#     if code == request.codes.ok:
#         data = (request.body.decode('utf-8'))
#         response_json = json.loads(data)
#
#         try:
#             yellow_obj = YellowUserToken.objects.get(webhook_id=webhook_id)
#             print(yellow_obj)
#             access_token = yellow_obj.yellowant_token
#             print(access_token)
#             integration_id = yellow_obj.yellowant_integration_id
#             service_application = str(integration_id)
#             print(service_application)
#
#
#             # Creating message object for webhook message
#             webhook_message = MessageClass()
#             id = str(response_json['eventNotifications'][0]['dataChangeEvent']['entities'][0]['id'])
#             webhook_message.message_text = "Invoice " + str(response_json['eventNotifications'][0]['dataChangeEvent']['entities'][0]['id']) + " updated"
#             attachment = MessageAttachmentsClass()
#             attachment.title = "Invoice operations"
#
#             button_get_incidents = MessageButtonsClass()
#             button_get_incidents.name = "1"
#             button_get_incidents.value = "1"
#             button_get_incidents.text = "Get invoice details"
#             button_get_incidents.command = {
#                 "service_application": service_application,
#                 "function_name": 'read_invoice',
#                 "data": {"invoice_id":id}
#             }
#
#             attachment.attach_button(button_get_incidents)
#             webhook_message.attach(attachment)
#             #print(integration_id)
#
#             webhook_message.data = {"invoice_id":id}
#             # Creating yellowant object
#             yellowant_user_integration_object = YellowAnt(access_token=access_token)
#
#             # Sending webhook message to user
#             send_message = yellowant_user_integration_object.create_webhook_message(
#                 requester_application=integration_id,
#                 webhook_name="invoice_update", **webhook_message.get_dict())
#
#             return HttpResponse("OK", status=200)
#
#         except YellowUserToken.DoesNotExist:
#             return HttpResponse("Not Authorized", status=403)
#     else:
#         return HttpResponse(status=400)
#
#
# def add_new_invoice(request,webhook_id):
#
#     """
#     Webhook function to notify user about newly created invoice
#     """
#     print("In add_new_invoice")
#
#
#     # Extracting necessary data
#     code = request.GET.get("code", False)
#
#     if code == request.codes.ok:
#         data = (request.body.decode('utf-8'))
#         response_json = json.loads(data)
#
#         try:
#             yellow_obj = YellowUserToken.objects.get(webhook_id=webhook_id)
#             print(yellow_obj)
#             access_token = yellow_obj.yellowant_token
#             print(access_token)
#             integration_id = yellow_obj.yellowant_integration_id
#             service_application = str(integration_id)
#             print(service_application)
#
#             # Creating message object for webhook message
#             webhook_message = MessageClass()
#             id = str(response_json['eventNotifications'][0]['dataChangeEvent']['entities'][0]['id'])
#             webhook_message.message_text = "New invoice added\n" + "ID :" + str(response_json['eventNotifications'][0]['dataChangeEvent']['entities'][0]['id'])
#             attachment = MessageAttachmentsClass()
#             attachment.title = "Invoice operations"
#
#             button_get_incidents = MessageButtonsClass()
#             button_get_incidents.name = "1"
#             button_get_incidents.value = "1"
#             button_get_incidents.text = "Read invoice"
#             button_get_incidents.command = {
#                 "service_application": service_application,
#                 "function_name": 'read_invoice',
#                 "data": {"invoice_id": id}
#             }
#
#
#             webhook_message.data = {"invoice_id":id}
#             attachment.attach_button(button_get_incidents)
#             webhook_message.attach(attachment)
#             #print(integration_id)
#
#             # Creating yellowant object
#             yellowant_user_integration_object = YellowAnt(access_token=access_token)
#
#             # Sending webhook message to user
#             send_message = yellowant_user_integration_object.create_webhook_message(
#                 requester_application=integration_id,
#                 webhook_name="new_invoice", **webhook_message.get_dict())
#
#             return HttpResponse("OK", status=200)
#
#         except YellowUserToken.DoesNotExist:
#             return HttpResponse("Not Authorized", status=403)
#     else:
#         return HttpResponse(status=400)
#
# def add_new_customer(request,webhook_id):
#
#     """
#     Webhook function to notify user about newly created customer
#     """
#     print("In add_new_customer")
#     print(webhook_id)
#     # Extracting necessary data
#
#     code = request.GET.get("code", False)
#
#     if code == request.codes.ok:
#         data = (request.body.decode('utf-8'))
#         response_json = json.loads(data)
#         print(response_json)
#
#         try:
#             yellow_obj = YellowUserToken.objects.get(webhook_id=webhook_id)
#             print(yellow_obj)
#             access_token = yellow_obj.yellowant_token
#             print(access_token)
#             integration_id = yellow_obj.yellowant_integration_id
#             #DropBoxUserToken.objects.get(realmId=response_json['eventNotifications'][0]['realmId']).user_integration_id
#             service_application = str(integration_id)
#             print(service_application)
#
#             # Creating message object for webhook message
#             webhook_message = MessageClass()
#             id = str(response_json['eventNotifications'][0]['dataChangeEvent']['entities'][0]['id'])
#             webhook_message.message_text = "New customer added\n" + "ID :" + str(response_json['eventNotifications'][0]['dataChangeEvent']['entities'][0]['id'])
#             attachment = MessageAttachmentsClass()
#             attachment.title = "Get all customer details"
#
#             button_get_incidents = MessageButtonsClass()
#             button_get_incidents.name = "1"
#             button_get_incidents.value = "1"
#             button_get_incidents.text = "Get customer details"
#             button_get_incidents.command = {
#                 "service_application": service_application,
#                 "function_name": 'get_customer_details',
#                 "data": {"customer_id": id}
#             }
#
#             attachment.attach_button(button_get_incidents)
#
#             webhook_message.data = {"customer_id":id}
#             webhook_message.attach(attachment)
#             #print(integration_id)
#
#             # Creating yellowant object
#             yellowant_user_integration_object = YellowAnt(access_token=access_token)
#
#             # Sending webhook message to user
#             send_message = yellowant_user_integration_object.create_webhook_message(
#                 requester_application=integration_id,
#                 webhook_name="new_customer", **webhook_message.get_dict())
#             return HttpResponse("OK", status=200)
#
#         except YellowUserToken.DoesNotExist:
#             return HttpResponse("Not Authorized", status=403)
#     else:
#         return HttpResponse(status=400)
#

@csrf_exempt
def yellowantapi(request):
    try:
        """
        Recieve user commands from YA
        """

        # Extracting the necessary data
        data = json.loads(request.POST['data'])
        args = data["args"]
        service_application = data["application"]
        verification_token = data['verification_token']
        function_name = data['function_name']
        # print(data)

        # Verifying whether the request is actually from YA using verification token
        if verification_token == settings.YELLOWANT_VERIFICATION_TOKEN:

        # Processing command in some class Command and sending a Message Object
            message = CommandCentre(data["user"], service_application, function_name, args).parse()
        # Appropriate function calls for corresponding webhook functions
            # Figure out

        # Returning message response
            return HttpResponse(message)
        else:
            # Handling incorrect verification token
            error_message = {"message_text": "Incorrect Verification token"}
            return HttpResponse(json.dumps(error_message), content_type="application/json")

    except Exception as e:
        # Handling exception
        print(str(e))
        traceback.print_exc()
        return HttpResponse("Something went wrong !")
