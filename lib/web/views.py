"""
Functions corresponding to URL patterns of web app

"""

#from django.http import HttpResponse
#from django.http import HttpResponseRedirect
#from django.shortcuts import render

import json
import requests
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render
from yellowant import YellowAnt
from ..records.models import YellowUserToken, DropBoxUserToken


def index(request, path):
    """ Loads the homepage of the app.
        index function loads the home.html page
    """
    #print('test')


    context = {
                "base_href": settings.BASE_HREF,
                "application_id": settings.YA_APP_ID,
                "user_integrations": []
             }

    # Check if user is authenticated otherwise redirect user to login page

    if request.user.is_authenticated:
        user_integrations = YellowUserToken.objects.filter(user=request.user.id)
        print(user_integrations)
        # for user_integration in user_integrations:
        #     context["user_integrations"].append(user_integration)

        return render(request, "home.html", context)
    else:
        return HttpResponse("Please login !")

def user_list_view(request):
    """
    userdetails function shows the vital integration details of the user

    """
    #print("in userdetails")
    user_integrations_list = []

    # Check if user is authenticated otherwise redirect user to login page
    if request.user.is_authenticated:
        user_integrations = YellowUserToken.objects.filter(user=request.user.id)
        print(user_integrations)
        for user_integration in user_integrations:
            try:
                smut = DropBoxUserToken.objects.get(user_integration=user_integration)
                print(smut)
                user_integrations_list.append({"user_invoke_name":user_integration.\
                                              yellowant_integration_invoke_name,
                                               "id":user_integration.id, "app_authenticated":True,
                                               "is_valid":True})
            except DropBoxUserToken.DoesNotExist:
                user_integrations_list.append({"user_invoke_name":user_integration.\
                                              yellowant_integration_invoke_name,
                                               "id":user_integration.id, "app_authenticated":False,
                                               "is_valid":False})
    return HttpResponse(json.dumps(user_integrations_list), content_type="application/json")

def user_detail_update_delete_view(request, id=None):
    """
    delete_integration function deletes the particular integration
    """

    #print("In user_detail_update_delete_view")
    #print(id)
    user_integration_id = id

    if request.method == "GET":
        pass
        # return user data
        # smut = DropBoxUserToken.objects.get(user_integration=user_integration_id)
        # return HttpResponse(json.dumps({
        #     "is_valid": True
        # }))

    elif request.method == "DELETE":
        print("Deleting integration")
        access_token_dict = YellowUserToken.objects.get(id=id)
        user_id = access_token_dict.user
        if user_id == request.user.id:
            access_token = access_token_dict.yellowant_token
            print(access_token)
            user_integration_id = access_token_dict.yellowant_integration_id
            print(user_integration_id)
            url = "https://api.yellowant.com/api/user/integration/%s" % (user_integration_id)
            yellowant_user = YellowAnt(access_token=access_token)
            print(yellowant_user)
            yellowant_user.delete_user_integration(id=user_integration_id)
            response = YellowUserToken.objects.get(yellowant_token=access_token).delete()
            print(response)
            return HttpResponse("successResponse", status=200)
        else:
            return HttpResponse("Not Authenticated", status=403)

    elif request.method == "PUT":
        pass
        # data = json.loads(request.body.decode("utf-8"))
        # print(data)
        # api_key = data['statuspage_api_key']
        # page_id = data['page_id']
        # user_integration = data['user_integration']
        #
        # headers = {
        #     "Authorization": "OAuth %s" % (api_key),
        #     "Content-Type": "application/json"
        # }
        #
        # url = "https://api.statuspage.io/v1/pages/" + page_id + ".json"
        # response = requests.get(url, headers=headers)
        #
        # if response.status_code == 200:
        #     print("Valid")
        #     sp_object = StatuspageUserToken.objects.get(user_integration_id=user_integration)
        #     print(sp_object.statuspage_access_token)
        #     sp_object.statuspage_access_token = api_key
        #     sp_object.statuspage_page = page_id
        #     sp_object.apikey_login_update_flag = True
        #     sp_object.save()
        #     print(sp_object.statuspage_access_token)
        #     return HttpResponse(json.dumps({
        #         "ok": True,
        #         "is_valid": True
        #     }))
        # else:
        #     print("Invalid")
        #     return HttpResponse(json.dumps({
        #         "ok": False,
        #         "is_valid": False
        #     }))
