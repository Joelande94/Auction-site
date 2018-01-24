"""YAAS_Andersson URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from YAAS.views import homepage, register, login, logout, loggedin, \
invalid_login, editUser, create_auction, my_auctions, view_auction, \
bid_auction, search, edit_auction, edit_email, delete_auction \
#confirm_create

from django.conf.urls import url
from django.contrib import admin


admin.autodiscover()

urlpatterns = [
    url(r'^admin/', admin.site.urls),

    url(r'^home', homepage, name="home"),

    url(r'^search', search),

    url(r'^create_auction', create_auction, name="create_auction"),
    #url(r'^confirm_create', confirm_create, name="confirm_create"),
    url(r'^accounts/auctions', my_auctions, name="my_auctions"),
    url(r'^edit_auction/(?P<auction_id>([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})+)', edit_auction, name="edit_auction"),
    url(r'^view_auction/(?P<auction_id>([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})+)', view_auction, name="view_auction"),
    url(r'^bid_auction/(?P<auction_id>([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})+)', bid_auction, name="bid_auction"),
    url(r'^delete_auction/(?P<auction_id>([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})+)', delete_auction, name="delete_auction"),

    #User auth urls
    url(r'^accounts/login', login, name="login"),
    url(r'^accounts/edit', editUser, name="edit"),
    url(r'^accounts/logout', logout),
    url(r'^accounts/loggedin', loggedin),
    url(r'^accounts/invalid', invalid_login),
    url(r'^register', register, name="register"),

    url(r'^edit_email', edit_email),

    url(r'^', homepage),
]
