import sys
import uuid
from datetime import date, datetime, time, timedelta
from itertools import chain
import pytz
from YAAS.models import Auction, Bid
from YAAS.serializers import AuctionSerializer
from celery.schedules import crontab
from celery.task import periodic_task
from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.postgres.search import SearchVector, SearchQuery
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, render_to_response, redirect
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import ugettext as _
from django.views.generic import View
from .forms import UserForm, EditPasswordForm, AuctionForm, BidOnAuctionForm

from django.core.exceptions import ObjectDoesNotExist

import threading
from smtplib import SMTPException
import pytz
from YAAS.models import Auction, Bid
from django.contrib.auth.models import User
from django.core.mail import send_mail, EmailMessage
from django.db.models import Q

'''REST bullshit'''
from rest_framework import serializers
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.decorators import renderer_classes
from django.core import serializers
'''REST bullshit'''

'''Exceptions'''


def update_auctions():
    criteria1 = Q(state="ACTIVE")
    criteria2 = Q(deadline__lt=datetime.now(pytz.utc))
    auctions = Auction.objects.filter(criteria1 & criteria2)
    print "length: " + str(len(auctions))
    for auction in auctions:
        auction.state = "ADJUDICATED"
        auction.save()
        try:
            print "hoi"
            top_bidder = User.objects.get(pk=auction.top_bidder)
            seller = User.objects.get(pk=auction.owner)
            if seller == top_bidder:
                print EmailMessage(
                    'Your auction has expired!',
                    'Your auction: "' + auction.title + '" has expired. '
                    "yaasdjango@gmail.com",
                    [seller.email],
                ).send()
                return 0
            print EmailMessage(
                'Your auction has been resolved!',                                                            #Subject
                'Your auction: "' + auction.title + '" has been resolved. ' + 'The winner of the auction is: '#Body
                + top_bidder.username + '. The end price was ' + str(auction.current_bid) + 'eur\n'           #Body
                + "The buyer's email is: " + top_bidder.email,                                                #Body
                "yaasdjango@gmail.com",                                                                       #Sender
                [seller.email],                                                                               #Receiver
            ).send()
            print EmailMessage(
                'You won an auction!',
                'You won the auction "' + auction.title + '". The end price was ' + str(auction.current_bid) + 'eur\n'
                "The seller's email is: " + seller.email,
                "yaasdjango@gmail.com",
                [top_bidder.email],
            ).send()
        except SMTPException:
            auction.state = "ERROR"
            auction.save()
            raise


def start_timer():
    timer = threading.Timer(60.0, update_auctions)
    timer.daemon = True
    timer.start()

start_timer()


# Create your views here.
def homepage(request):
    '''LANGUAGE SETTINGS'''
    session_language = 'en-gb'
    if 'lang' in request.session:
        session_language = request.session['lang']
    '''LANGUAGE SETTINGS'''

    auctions = Auction.objects.filter(deadline__gt=datetime.now(pytz.utc))
    auctions = auctions.filter(state="ACTIVE")

    context = {'auctions': auctions,
               'session_language': session_language,
               'username': request.user.username}

    if 'message' in request.session:
        context.__setitem__('message', request.session['message'])
        del request.session['message']
    return render(request, "homepage.html", context)


'''User authentication'''
def login(request):
    '''LANGUAGE SETTINGS'''
    session_language = 'en-gb'

    if 'lang' in request.session:
        session_language = request.session['lang']
    '''LANGUAGE SETTINGS'''

    if request.user.is_authenticated:
        request.session['message'] = "You're already logged in"
        return HttpResponseRedirect(reverse("home"))

    if request.method == "POST":
        print "post"
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return HttpResponseRedirect('/accounts/loggedin')
        else:
            return HttpResponseRedirect('/accounts/invalid')
    context = {'username': request.user.username, }
    if 'message' in request.session:
        context = {'username': request.user.username,
                   'message': request.session['message'], }
        del request.session['message']
    return render(request, "login.html", context)


def logout(request):
    auth.logout(request)
    request.session['message'] = "Logged out"
    return HttpResponseRedirect(reverse("home"))


def loggedin(request):
    session_language = 'en-gb'

    if 'lang' in request.session:
        session_language = request.session['lang']

    context = {'username': request.user.username, }

    return render(request, 'loggedin.html', context)


def invalid_login(request):
    request.session['message'] = "Incorrect credentials."
    return HttpResponseRedirect(reverse('login'))


def register(request):
    '''LANGUAGE SETTINGS'''
    session_language = 'en-gb'
    if request.user.is_authenticated:
        request.session['message'] = "You're already logged in"
        return HttpResponseRedirect(reverse('home'))

    if 'lang' in request.session:
        session_language = request.session['lang']
    '''LANGUAGE SETTINGS'''

    form = UserForm(request.POST or None)
    if form.is_valid():
        print "register2"
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        password2 = form.cleaned_data['password2']
        email = form.cleaned_data['email']
        if password == password2:
            user = User.objects.create_user(username, email, password)
            user.set_password(password)
            user.save()
            user = auth.authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    auth.login(request, user)
                    request.session['message'] = "Account created."
                    return HttpResponseRedirect(reverse("home"))
            else:
                request.session['message'] = "Looks like that username is taken"
                return HttpResponseRedirect(reverse("register"))
        else:
            request.session['message'] = "Passwords did not match."
            return HttpResponseRedirect(reverse(register))

    context = {
        "form": form,
        "message": "That username is taken",
        "session_language": session_language
    }
    return render(request, 'register.html', context)

'''User authentication'''


'''User stuff'''
def editUser(request):
    '''LANGUAGE SETTINGS'''
    session_language = 'en-gb'

    if 'lang' in request.session:
        session_language = request.session['lang']
    '''LANGUAGE SETTINGS'''

    form = EditPasswordForm(request.POST or None)
    if form.is_valid():
        old_user = auth.authenticate(username=request.user.username, password=form.cleaned_data['old_password'])
        password = form.cleaned_data['new_password']
        password2 = form.cleaned_data['new_password2']
        if old_user is not None:
            if password == password2:
                if old_user.is_active:
                    user = request.user
                    user.set_password(password)
                    user.save()
                    auth.login(request, user)
                    request.session['message'] = "Password changed"
                    return HttpResponseRedirect(reverse('home'))
                else:
                    request.session['message'] = "User is inactive..."
                    return HttpResponseRedirect(reverse('edit'))
            else:
                request.session['message'] = "passwords didn't match"
                return HttpResponseRedirect(reverse('edit'))
        else:
            request.session['message'] = "Old password was incorrect"
            return HttpResponseRedirect(reverse('edit'))
    context = {'form': form,
               'email': request.user.email,
               'username': request.user.username,
               'session_language': session_language}

    if 'message' in request.session:
        context = {'username': request.user.username,
                   'message': request.session['message'],
                   'form': form,
                   'session_language': session_language }
        del request.session['message']

    return render(request, 'editUser.html', context)


def edit_email(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            if 'email' in request.POST:
                user = request.user
                user.email = request.POST['email']
                user.save()
                request.session['message'] = "Email successfully edited"
            else:
                request.session['message'] = "Faulty form"
        else:
            request.session['message'] = "Illegal request type"
    else:
        request.session['message'] = "You need to be logged in to do that."
    return HttpResponseRedirect(reverse('home'))


'''User stuff'''


def create_auction(request):
    '''LANGUAGE SETTINGS'''
    session_language = 'en-gb'
    if 'lang' in request.session:
        session_language = request.session['lang']
    '''LANGUAGE SETTINGS'''
    form = AuctionForm(request.POST or None)
    if request.method == "GET":
        print "GET"
        context = {'form': form,
                   'username': request.user.username,
                   'session_language': session_language}
        if 'message' in request.session:
            context.__setitem__('message', request.session['message'])
            del request.session['message']
        return render(request, 'addAuction.html', context)

    if request.method == "POST":
        print "POST"
        try:
            if form.is_valid():
                if 'confirm_create' in request.POST:
                    if request.POST['confirm_create'] == "yes":
                        title = form.cleaned_data['title']
                        description = form.cleaned_data['description']
                        deadline = form.cleaned_data['deadline']

                        temp = datetime.now(pytz.utc) + timedelta(hours=deadline)
                        deadline = datetime(temp.year, temp.month, temp.day, temp.hour, temp.minute, tzinfo=pytz.utc)
                        current_bid = form.cleaned_data['price']

                        Auction(title=title, owner=request.user.id, seller=request.user.username, description=description,
                                current_bid=current_bid, deadline=deadline, top_bidder=request.user.id).save()
                        email = request.user.email
                        print EmailMessage(
                            'Auction created',                                         # Subject
                            'Your auction: "' + title + '" for '                       # Body
                            + str(current_bid) + 'eur' + ' has been created',           # Body
                            "yaasdjango@gmail.com",                                    # Sender
                            [email],                                                   # Receiver
                        ).send()

                        request.session['message'] = "Auction created"
                        return HttpResponseRedirect(reverse('home'))

                    elif request.POST['confirm_create'] == "no":
                        return HttpResponseRedirect(reverse('home'))

                title = form.cleaned_data['title']
                description = form.cleaned_data['description']
                deadline = form.cleaned_data['deadline']
                current_bid = form.cleaned_data['price']

                print "Description 1: " + description
                context = {'username': request.user.username,
                           'session_language': session_language,
                           'form_title': title,
                           'form_description': description,
                           'form_deadline': deadline,
                           'form_price': current_bid}
                if 'message' in request.session:
                    context.__setitem__('message', request.session['message'])
                    del request.session['message']
                return render(request, "confirm_create.html", context)

            else:
                request.session['message'] = "Form not valid"
                return HttpResponseRedirect(reverse('home'))

        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise
    request.session['message'] = "Invalid request method"
    return HttpResponseRedirect(reverse('home'))


def my_auctions(request):
    '''LANGUAGE SETTINGS'''
    session_language = 'en-gb'
    if 'lang' in request.session:
        session_language = request.session['lang']
    '''LANGUAGE SETTINGS'''

    context = {'username': request.user.username,
               'session_language': session_language,
               'auctions': Auction.objects.filter(owner=request.user.id)}
    if 'message' in request.session:
        context.__setitem__('message', request.session['message'])
        del request.session['message']

    return render(request, 'my_auctions.html', context)


def edit_auction(request, auction_id):
    '''LANGUAGE SETTINGS'''
    session_language = 'en-gb'
    if 'lang' in request.session:
        session_language = request.session['lang']
    '''LANGUAGE SETTINGS'''

    context = {'username': request.user.username,
               'session_language': session_language}

    if str(request.user.id) == str(Auction.objects.get(pk=auction_id).owner):
        form = AuctionForm(request.POST or None)
        if request.method == "POST":
            if request.session['viewing_auction_description'] == Auction.objects.get(pk=auction_id).description \
                    and request.session['viewing_auction_title'] == Auction.objects.get(pk=auction_id).description:

                auction = Auction.objects.get(pk=auction_id)
                auction.description = form.description
                auction.title = form.title
                request.session['message'] = "Successfully edited auction"
                auction.save()
            return HttpResponseRedirect(reverse('home'))

        request.session['viewing_auction_description'] = Auction.objects.get(pk=auction_id).description
        request.session['viewing_auction_title'] = Auction.objects.get(pk=auction_id).title

        auction = Auction.objects.get(pk=auction_id)
        form = AuctionForm(initial={'title': auction.title, 'description': auction.description, 'price': auction.current_bid})

        context.__setitem__('form', form)

        if 'message' in request.session:
            context.__setitem__('message', request.session['message'])
            del request.session['message']
        return render(request, "edit_auction.html", context)

    else:
        request.session['message'] = "You may not edit this auction"
        return HttpResponseRedirect(reverse('home'))


def view_auction(request, auction_id):
    try:
        auction = Auction.objects.get(pk=auction_id)
    except ObjectDoesNotExist:
        request.session['message'] = 'Auction not found'
        return HttpResponseRedirect(reverse('home'))

    if auction.deadline > datetime.now(pytz.utc):
        request.session['viewing_auction_description'] = Auction.objects.get(pk=auction_id).description
        request.session['viewing_auction_title'] = Auction.objects.get(pk=auction_id).title

        form = BidOnAuctionForm(None)
        context = {'auction': auction,
                   'deadline': auction.deadline.strftime("%Y-%m-%d %H:%M:%S"),
                   'username': request.user.username,
                   'user_id': request.user.id,
                   'form': form}
        if 'message' in request.session:
            print "Message found: " + request.session['message']
            context.__setitem__('message', request.session['message'])
            del request.session['message']
        return render(request, 'view_auction.html', context)
    elif auction.owner == request.user.id:
        return HttpResponseRedirect(reverse('edit_auction'))
    request.session['message'] = 'This auction has expired'
    return HttpResponseRedirect(reverse('home'))


def bid_auction(request, auction_id):
    if request.user.is_authenticated:
        owner = Auction.objects.get(pk=auction_id).owner
        if str(request.user.id) != owner and str(request.user.id) != Auction.objects.get(pk=auction_id).top_bidder:
            if request.method == "POST":
                form = BidOnAuctionForm(request.POST)
                if form.is_valid():
                    bid = form.cleaned_data['bid']
                    auction = Auction.objects.get(pk=auction_id)
                    if bid > auction.current_bid and request.session['viewing_auction_description']\
                            == Auction.objects.get(pk=auction_id).description and request.session['viewing_auction_title']\
                            == Auction.objects.get(pk=auction_id).title:
                        if Auction.objects.get(pk=auction_id).deadline > datetime.now(pytz.utc):
                            Bid(auction_id=auction_id, bidder=request.user.id, bid=bid).save()
                            auction.top_bidder = request.user.id
                            auction.current_bid = bid
                            auction.save()

                            form = BidOnAuctionForm(None)
                            context = {'auction': Auction.objects.get(pk=auction_id),
                                       'username': request.user.username,
                                       'deadline': auction.deadline.strftime("%Y-%m-%d %H:%M:%S"),
                                       'message': "Bid placed",
                                       'form': form}
                            return render(request, "view_auction.html", context)
                        else:
                            request.session['message'] = "The auction has expired"
                            return HttpResponseRedirect(reverse('home'))
                    else:
                        form = BidOnAuctionForm(None)
                        context = {'auction': Auction.objects.get(pk=auction_id),
                                   'username': request.user.username,
                                   'deadline': auction.deadline.strftime("%Y-%m-%d %H:%M:%S"),
                                   'message': "Either your bid was too low or "
                                              "the owner of the auction changed something.",
                                   'form': form}
                        return render(request, "view_auction.html", context)
                else:
                    form = BidOnAuctionForm(None)
                    context = {'username': request.user.username,
                               'auction': Auction.objects.get(pk=auction_id),
                               'deadline': Auction.objects.get(pk=auction_id).deadline.strftime("%Y-%m-%d %H:%M:%S"),
                               'message': "form not valid",
                               'form': form}
                    return render(request, "view_auction.html", context)

            request.session['message'] = "Illegal method request type"
            return HttpResponseRedirect(reverse('home'))
        else:
            request.session['message'] = "You're already the highest bidder/the owner of that auction"
            return HttpResponseRedirect(reverse('home'))
    else:
        request.session['message'] = 'You need to log in before bidding'
        return HttpResponseRedirect(reverse('home'))


def delete_auction(request, auction_id):
    print "delete: " + auction_id
    auction = Auction.objects.get(pk=auction_id)
    bids = Bid.objects.filter(auction_id=auction_id)
    for bid in bids:
        bid.delete()
    auction.delete()
    request.session['message'] = "Auction deleted"
    return HttpResponseRedirect(reverse('home'))

def search(request):
    '''LANGUAGE SETTINGS'''
    session_language = 'en-gb'
    if 'lang' in request.session:
        session_language = request.session['lang']
    '''LANGUAGE SETTINGS'''
    context = {'username': request.user.username,
               'session_language': session_language,}
    query = request.POST['query']
    print query
    search_words = query.split()
    search_result = list()
    for word in search_words:
        temp = list(chain(search_result, Auction.objects.filter(description__contains=word, deadline__gt=datetime.now(pytz.utc))))
        temp = list(chain(temp, Auction.objects.filter(title__contains=word, deadline__gt=datetime.now(pytz.utc))))
        for result in temp:
            if not search_result.__contains__(result):
                search_result.append(result)

    context.__setitem__('auctions', search_result)
    if len(search_result) == 0:
        context.__setitem__('message', "Found nothing...")
    return render(request, "search_result.html", context)