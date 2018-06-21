""" This is the command centre for all the commands created in the YA developer console
    This file contains the logic to understand a user message request from YA
    and return a response in the format of a YA message object accordingly

"""

#from django.http import HttpResponse
#from yellowant import YellowAnt
import json
import urllib
from decimal import Decimal, ROUND_DOWN

import datetime
from yellowant.messageformat import MessageClass, MessageAttachmentsClass, AttachmentFieldsClass, MessageButtonsClass

from .models import YellowUserToken,DropBoxUserToken
#import traceback
import requests
#import datetime
#import pytz
from django.conf import settings

class CommandCentre(object):

    """ Handles user commands

        Args:
            yellowant_integration_id (int): The integration id of a YA user
            function_name (str): Invoke name of the command the user is calling
            args (dict): Any arguments required for the command to run
    """
    def __init__(self, yellowant_user_id, yellowant_integration_id, function_name, args):
        self.yellowant_user_id = yellowant_user_id
        self.yellowant_integration_id = yellowant_integration_id
        self.function_name = function_name
        self.args = args

    def parse(self):
        """
        Matching which function to call
        """

        self.commands = {
            'get_account_info' : self.get_account_info,
            'get_all_shared_folders' : self.get_all_shared_folders,
            'get_all_file_requests': self.get_all_file_requests,
            'get_space_usage' : self.get_space_usage,
            'get_shared_links': self.get_shared_links,
            'get_all_folders' : self.get_all_folders,
            'get_more_folders': self.get_more_folders,
            'download_file' : self.download_file,
            'search' : self.search,
            'share_folder' : self.share_folder,
            'create_folder' : self.create_folder,
        }

        self.user_integration = YellowUserToken.objects.get\
            (yellowant_integration_id=self.yellowant_integration_id)

        self.dropbox_user_token_object = DropBoxUserToken.objects.\
            get(user_integration=self.user_integration)

        self.account_id = self.dropbox_user_token_object.account_id

        self.dropbox_access_token = self.dropbox_user_token_object.\
            accessToken


        return self.commands[self.function_name](self.args)



    def get_account_info(self,args):

        print("In get_company_info")
        endpoint = "https://api.dropboxapi.com/2/users/get_account"

        # API parameteres for getting account information

        headers = {
            'Authorization': 'Bearer ' + self.dropbox_access_token,
            'Content-Type': 'application/json',
        }

        data = {"account_id": str(self.account_id)}

        # Consuming the API
        r = requests.post('https://api.dropboxapi.com/2/users/get_account', headers=headers, json=data)

        # Response check
        if r.status_code == requests.codes.ok:

            # Getting response in JSON
            response = r.content.decode("utf-8")
            response = json.loads(response)

            # Creating message objects to structure the message to be shown
            message = MessageClass()
            message.message_text = "User Account Details :"

            attachment = MessageAttachmentsClass()

            field1 = AttachmentFieldsClass()
            field1.title = "Name :"
            field1.value = response["name"]["display_name"]
            attachment.attach_field(field1)


            field2 = AttachmentFieldsClass()
            field2.title = "E-mail :"
            field2.value = response["email"]
            attachment.attach_field(field2)
            attachment.image_url = response["profile_photo_url"]

            message.attach(attachment)
            return message.to_json()
        else:
            m = MessageClass()
            print(r.content.decode("utf-8"))
            d = r.content.decode("utf-8")
            m.message_text = "{0}: {1}".format(r.status_code, r.text)
            return m.to_json()

    def get_all_shared_folders(self,args):

        print("In get_all_shared_folders")

        endpoint = "https://api.dropboxapi.com/2/sharing/list_folders"
        headers = {
            'Authorization': 'Bearer ' + str(self.dropbox_access_token),
            'Content-Type': 'application/json',
        }

        data = {"limit": 100,"actions": []}

        # Consuming the API
        r = requests.post(endpoint, headers=headers, json=data)

        # Response check
        if (r.status_code == requests.codes.ok):
            response = r.content.decode("utf-8")
            response = json.loads(response)
            print(response)

            #Creating message from YA SDK
            message = MessageClass()
            message.message_text = "All shared file details :"

            attachment = MessageAttachmentsClass()

            for i in range(0,len(response['entries'])):
                field1 = AttachmentFieldsClass()
                field1.title = "Name :"
                field1.value = response['entries'][i]['name']
                attachment.attach_field(field1)

                field2 = AttachmentFieldsClass()
                field2.title = "Preview URL :"
                field2.value = response['entries'][i]['preview_url']
                attachment.attach_field(field2)

            message.attach(attachment)
            return message.to_json()
        else:
            m = MessageClass()
            print(r.content.decode("utf-8"))
            d = r.content.decode("utf-8")
            m.message_text = "{0}: {1}".format(r.status_code, r.text)
            return m.to_json()

    def get_all_file_requests(self,args):

        print("In get_all_file_requests")

        # API call parameters for creating an invoice
        headers = {
            'Authorization': 'Bearer ' + str(self.dropbox_access_token),
        }

        # Consuming the API
        r = requests.post('https://api.dropboxapi.com/2/file_requests/list', headers=headers)

        # Response check
        if r.status_code == requests.codes.ok:
            response = r.content.decode("utf-8")
            response = json.loads(response)
            print(response)

            # Creating message from YA SDK
            message = MessageClass()
            attachment = MessageAttachmentsClass()

            if len(response) == 0:
                message.message_text = "No File Requests"
                message.attach(attachment)
                return message.to_json()
            else:
                message.message_text = "All file requests :"
                message.attach(attachment)
                return message.to_json()

        else:
            m = MessageClass()
            print(r.content.decode("utf-8"))
            d = r.content.decode("utf-8")
            m.message_text = "{0}: {1}".format(r.status_code, r.text)
            return m.to_json()


    def get_space_usage(self,args):

        print("In get_space_usage")

        headers = {
            'Authorization': 'Bearer ' + str(self.dropbox_access_token),
        }

        # Consuming the API
        r = requests.post('https://api.dropboxapi.com/2/users/get_space_usage', headers=headers)

        # Response check
        if r.status_code == requests.codes.ok:

            # Fetching response in JSON
            response = r.content.decode("utf-8")
            response = json.loads(response)
            print(response)

            #Creating a message object from YA SDK
            message = MessageClass()
            message.message_text = "Space usage/allocation details :"

            attachment = MessageAttachmentsClass()

            used_gb = float(response['used']/1000000000)
            allocated_gb = float(response['allocation']['allocated']/1000000000)



            field1 = AttachmentFieldsClass()
            field1.title = "Used : "
            field1.value = str(Decimal(str(used_gb)).quantize(Decimal('.01'), rounding=ROUND_DOWN)) + " gb"
            attachment.attach_field(field1)

            field2 = AttachmentFieldsClass()
            field2.title = "Allocated : "
            field2.value = str(Decimal(str(allocated_gb)).quantize(Decimal('.01'), rounding=ROUND_DOWN)) + " gb"
            attachment.attach_field(field2)

            message.attach(attachment)
            return message.to_json()


        else:
            m = MessageClass()
            print(r.content.decode("utf-8"))
            d = r.content.decode("utf-8")
            m.message_text = "{0}: {1}".format(r.status_code, r.text)
            return m.to_json()


    def get_shared_links(self,args):

        print("In get_shared_links")

        flag = False
        # Arguments passed from slack
        # For the optional argument
        try:
            path = args['path']
            flag = True
        except:
            flag = False

        headers = {
            'Authorization': 'Bearer ' + self.dropbox_access_token,
            'Content-Type': 'application/json',
        }


        endpoint = 'https://api.dropboxapi.com/2/sharing/list_shared_links'

        if flag == True:
            data = {"path": path}
        else:
            data = {}

        # Consuming the API
        r = requests.post(endpoint, headers=headers, json=data)

        # Response check
        if r.status_code == requests.codes.ok:

            # Getting response in JSON
            response = r.content.decode("utf-8")
            response = json.loads(response)
            print(response)
            links = response['links']

            message = MessageClass()
            message.message_text = "List of all shared links :"
            attachment = MessageAttachmentsClass()

            for i in range(0,len(links)):
                try:
                    field1 = AttachmentFieldsClass()
                    field1.title = "Name :"
                    field1.value = links[i]['name']
                    attachment.attach_field(field1)
                except KeyError : 'name'

                # field2 = AttachmentFieldsClass()
                # field2.title = "Type :"
                # field2.value = links[i]['.tag']
                # attachment.attach_field(field2)

                field3 = AttachmentFieldsClass()
                field3.title = "Preview URL :"
                field3.value = links[i]['url']
                attachment.attach_field(field3)

            message.attach(attachment)
            return message.to_json()
        else:
            m = MessageClass()
            print(r.content.decode("utf-8"))
            d = r.content.decode("utf-8")
            m.message_text = "{0}: {1}".format(r.status_code, r.text)
            return m.to_json()

    def get_all_folders(self,args):

        print("In get_all_folders")

        # API call parameters for getting all customers

        headers = {
            'Authorization': 'Bearer ' + self.dropbox_access_token,
            'Content-Type': 'application/json',
        }

        data = {"path": "",
               "recursive": True,
               "include_media_info": False,
               "include_deleted": False,
               "include_has_explicit_shared_members": False,
               "include_mounted_folders": True}

        # Consuming the API
        r = requests.post('https://api.dropboxapi.com/2/files/list_folder', headers=headers, json=data)

        # Error check
        if r.status_code == requests.codes.ok:

            # Getting response in JSON format
            response = r.content.decode("utf-8")
            response = json.loads(response)
            print(response)

            message = MessageClass()
            message.message_text = "List of all folders :"
            attachment = MessageAttachmentsClass()

            for i in range(0, len(response['entries'])):

                field1 = AttachmentFieldsClass()
                field1.title = "Name :"
                field1.value = response['entries'][i]['name']
                attachment.attach_field(field1)

                field2 = AttachmentFieldsClass()
                field2.title = "Type :"
                field2.value = response['entries'][i]['.tag']
                attachment.attach_field(field2)
            #
            # if response['has_more'] == True:
            #     button = MessageButtonsClass()
            #     button.name = "1"
            #     button.value = "1"
            #     button.text = "Get more files and folders"
            #     button.command = {
            #         "service_application": self.user_integration,
            #         "function_name": 'get_more_folders',
            #         "data": {"cursor": response['cursor']}
            #     }
            #     attachment.attach_button(button)

            message.attach(attachment)
            return message.to_json()
        else:
            m = MessageClass()
            print(r.content.decode("utf-8"))
            d = r.content.decode("utf-8")
            m.message_text = "{0}: {1}".format(r.status_code, r.text)
            return m.to_json()

    ## Not an active function, used inside other function
    def get_more_folders(self,args):

        print("In 	get_more_folders")

        # Fetching arguments passed from Slack
        cursor = args['cursor']

        # API call parameters for getting customer details
        headers = {
            'Authorization': 'Bearer ' + self.dropbox_access_token,
            'Content-Type': 'application/json',
        }

        data = {"cursor": cursor}
        re = requests.post('https://api.dropboxapi.com/2/files/list_folder/continue', headers=headers,
                           json=data)

        if re.status_code == requests.codes.ok:

            res = re.content.decode("utf-8")
            res = json.loads(res)
            print("----")
            print(res)
        else:
            m = MessageClass()
            print(re.content.decode("utf-8"))
            d = re.content.decode("utf-8")
            m.message_text = "{0}: {1}".format(re.status_code, re.text)
            return m.to_json()

    def download_file(self,args):
        print("In download_file")
        # Fetching the arguments passed from slack
        path = args['path']

        # API call parameters for creating a customer

        headers = {
            'Authorization': 'Bearer ' + self.dropbox_access_token,
            'Content-Type': 'application/json',
        }

        data = {"path": path}

        # Consuming the API
        r = requests.post('https://api.dropboxapi.com/2/files/get_temporary_link', headers=headers, json=data)

        # Response check
        if (r.status_code == requests.codes.ok):

            # Getting the response
            response = r.content.decode("utf-8")
            response = json.loads(response)
            print(response)

            # Creating message using YA SDK
            message = MessageClass()
            message.message_text = "Temporary link to download :"
            attachment = MessageAttachmentsClass()

            field1 = AttachmentFieldsClass()
            field1.title = "This link expires in 4 Hr :"
            field1.value = response['link']
            attachment.attach_field(field1)

            message.attach(attachment)
            return message.to_json()
        else:
            m = MessageClass()
            print(r.content.decode("utf-8"))
            d = r.content.decode("utf-8")
            m.message_text = "{0}: {1}".format(r.status_code, r.text)
            return m.to_json()

    ## Handle more than 100 searches
    def search(self,args):
        print("In search")
        print(args)

        path = args['path']
        query = args['search']

        headers = {
            'Authorization': 'Bearer ' + self.dropbox_access_token,
            'Content-Type': 'application/json',
        }

        if path == '/':
            path = ""

        data = {"path": path,"query": query,"start": 0,"max_results": 100,"mode": "filename"}


        # Consuming the API
        r = requests.post('https://api.dropboxapi.com/2/files/search', headers=headers, json=data)

        # Response check
        if r.status_code == requests.codes.ok:
            print("---------------")
            # Getting response in JSON
            r = r.content.decode("utf-8")
            response = json.loads(r)
            print(response)

            # Creating message using YA SDK
            message = MessageClass()

            if len(response['matches']) == 0:
                message.message_text = "No matches !\nPlease search again."
                return message.to_json()

            message.message_text = "Matches :"
            attachment = MessageAttachmentsClass()

            for i in range(0, len(response['matches'])):

                field1 = AttachmentFieldsClass()
                field1.title = "Path:"
                field1.value = response['matches'][i]['metadata']['path_display']
                attachment.attach_field(field1)

                field2 = AttachmentFieldsClass()
                field2.title = "Name :"
                field2.value = response['matches'][i]['metadata']['name']
                attachment.attach_field(field2)

                field3 = AttachmentFieldsClass()
                field3.title = "Type :"
                field3.value = response['matches'][i]['metadata']['.tag']
                attachment.attach_field(field3)

            message.attach(attachment)
            return message.to_json()
        else:
            print("Error")
            m = MessageClass()
            print(r.content.decode("utf-8"))
            d = r.content.decode("utf-8")
            m.message_text = "{0}: {1}".format(r.status_code, r.text)
            return m.to_json()

    def share_folder(self, args):


        print("In share_folder")

        # Arguments from slack
        path = args["path"]
        member_policy = args['member_policy']
        shared_link_policy = args['shared_link_policy']

        if member_policy != 'anyone' and member_policy != "team":
            m = MessageClass()
            m.message_text = "Invalid value in member_policy argument"
            return m.to_json()

        if shared_link_policy != 'anyone' and shared_link_policy != "team":
            m = MessageClass()
            m.message_text = "Invalid value in shared_link_policy argument"
            return m.to_json()

        # API call parameters for getting all customer ids
        headers = {
            'Authorization': 'Bearer ' + self.dropbox_access_token,
            'Content-Type': 'application/json',
        }

        data = {"path": path,"acl_update_policy": "editors","force_async": False,"member_policy": member_policy ,"shared_link_policy": shared_link_policy}


        # Consuming the API
        r = requests.post('https://api.dropboxapi.com/2/sharing/share_folder', headers=headers, json=data)

        # Response check
        if r.status_code == requests.codes.ok:

            # Fetching response in JSON
            r = r.content.decode("utf-8")
            response = json.loads(r)
            print(response)

            # Creating a message object using YA SDK functions
            m = MessageClass()
            m.message_text = "Details for the shared folder : "
            attachment = MessageAttachmentsClass()

            field1 = AttachmentFieldsClass()
            field1.title = "Shared link : "
            field1.value = response['preview_url']
            attachment.attach_field(field1)

            field2 = AttachmentFieldsClass()
            field2.title = "Visibility :"
            field2.value = response['policy']['shared_link_policy']['.tag']
            attachment.attach_field(field2)

            field3 = AttachmentFieldsClass()
            field3.title = "Name :"
            field3.value = response['name']
            attachment.attach_field(field3)
            m.attach(attachment)
            return m.to_json()

        else:
            print("Error")
            m = MessageClass()
            print(r.content.decode("utf-8"))
            d = r.content.decode("utf-8")
            m.message_text = "{0}: {1}".format(r.status_code, r.text)
            return m.to_json()

    ## Check the button part
    def create_folder(self, args):

        print("In create_folder")
        print(args)

        path = args['path']
        autorename = args['autorename']

        if autorename != 'true' and autorename != 'false':
            m = MessageClass()
            m.message_text = "Invalid value in autorename argument"
            return m.to_json()

        headers = {
            'Authorization': 'Bearer ' + self.dropbox_access_token,
            'Content-Type': 'application/json',
        }

        if autorename == 'true':
            autorename = True
        else:
            autorename = False

        data = {"path": path,"autorename": autorename}



        # Consuming the API
        r = requests.post('https://api.dropboxapi.com/2/files/create_folder_v2', headers=headers, json=data)

        # Response check
        if r.status_code == requests.codes.ok:
            print("---------------")
            # Getting response in JSON
            r = r.content.decode("utf-8")
            response = json.loads(r)
            print(response)

            #Creating message using YA SDK
            message = MessageClass()
            attachment = MessageAttachmentsClass()

            message.message_text = "New folder successfully created"
            # button = MessageButtonsClass()
            # button.name = "1"
            # button.value = "1"
            # button.text = "Get folder details"
            # button.command = {
            #     "service_application": self.user_integration,
            #     "function_name": 'get_all_folders',
            #     "data" :{"path": response['metadata']['path_display'],
            #    "recursive": True,
            #    "include_media_info": False,
            #    "include_deleted": False,
            #    "include_has_explicit_shared_members": False,
            #    "include_mounted_folders": True}
            # }
            # attachment.attach_button(button)

            message.attach(attachment)
            return message.to_json()
        else:
            print("Error")
            m = MessageClass()
            print(r.content.decode("utf-8"))
            d = r.content.decode("utf-8")
            m.message_text = "{0}: {1}".format(r.status_code, r.text)
            return m.to_json()
