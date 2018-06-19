"""dropboxapp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.urls import include
from django.urls import path

from web import urls as web_urls
from records.views import redirectToYellowAntAuthenticationPage, yellowantRedirecturl, dropboxRedirecturl, yellowantapi

urlpatterns = [
    path('admin/', admin.site.urls),
    # For creating new integration
    url(r'^create-new-integration/', redirectToYellowAntAuthenticationPage,
        name="quickbook-ya-auth-redirect"),

    # For redirecting from yellowant
    url(r'^yellowantredirecturl/', yellowantRedirecturl,
        name="yellowant-auth-redirect"),

    # For redirecting to dropbox auth
    url(r'^dropbox-redirect-url/', dropboxRedirecturl, name="dropboxRedirecturl"),

    # url(r'^quickauth/',quickauth,name="quickauth"),

    # For redirecting to yellowant authentication page
    url("yellowantauthurl/", redirectToYellowAntAuthenticationPage,
        name="yellowant-auth-url"),

    # For getting command specific information from slack on executing a command
    url("yellowant-api/", yellowantapi, name="yellowant-api"),

    #url('webhook/(?P<hash_str>[^/]+)/', webhook, name='webhook'),
    ## url("",include(quickauth_urls)),
    url("", include(web_urls)),

]
