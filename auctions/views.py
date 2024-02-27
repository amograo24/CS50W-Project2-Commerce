from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms

from .models import User,Listing,Bidding,Comment,WatchList,Category
import datetime

class CreateListing(forms.ModelForm):
    class Meta:
        model=Listing
        fields=['item_name', 'item_description', 'item_category', 'image_url', 'price','date']
        widgets = {'date': forms.HiddenInput()}

class CreateBid(forms.ModelForm):
    class Meta:
        model=Bidding
        fields=['bid', 'time']
        widgets = {'time': forms.HiddenInput()}

class CreateComment(forms.ModelForm):
    class Meta:
        model=Comment
        fields=['comment','time_of_comment']
        widgets={'time_of_comment': forms.HiddenInput()}



def index(request):
    return render(request, "auctions/index.html",{
        "listings":Listing.objects.all()
    })

def closed_listings(request):
    return render(request, "auctions/closed_listings.html",{
        "listings":Listing.objects.all()
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user_watchlist=WatchList.objects.create(user=user)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


def create_listing(request):
    if request.method=="POST":
        form=CreateListing(request.POST)
        if form.is_valid():
            item_name=form.cleaned_data['item_name']
            item_description=form.cleaned_data['item_description']
            image_url=form.cleaned_data['image_url']
            starting_bid=form.cleaned_data['price']
            item_category=form.cleaned_data['item_category']
            date=datetime.datetime.now()
            creator=request.user
            if starting_bid>=0:
                listing=Listing(item_name=item_name,item_description=item_description,price=starting_bid,image_url=image_url,item_category=item_category,date=date,creator=creator) #,user=user
                listing.save()
                return HttpResponseRedirect(reverse("index"))
            else:
                return render(request,"auctions/create_listing.html",{
                    "content_listing":form,
                    "error":"The starting bid must be greater than or equal to zero."
                })
        else:
            return render(request,"auctions/create_listing.html",{
                "content_listing":form
            }) 
    return render(request,"auctions/create_listing.html",{
        "content_listing":CreateListing()
    })
    

def comment(request,listing_id):
    listing=Listing.objects.get(pk=listing_id)
    if request.method=="POST":
        form=CreateComment(request.POST)
        comment=request.POST['comment']
        commenter=request.user
        time=datetime.datetime.now()
        comment_data=Comment(time_of_comment=time,comment=comment,commenter=commenter,listing_commented=listing)
        comment_data.save()
        return HttpResponseRedirect(reverse("listing",args=(listing.id,)))

def watchlist_add_del(request,listing_id):
    listing=Listing.objects.get(pk=listing_id)
    if request.method=="POST":
        try:
            user_watchlist=WatchList.objects.get(user=request.user)
        except:
            user_watchlist=WatchList.objects.create(user=request.user)
        if listing in user_watchlist.listings.all():
            user_watchlist.listings.remove(listing)
            user_watchlist.save()
        else:
            user_watchlist.listings.add(listing)
            user_watchlist.save()
    return HttpResponseRedirect(reverse("listing",args=(listing.id,)))

def listing(request,listing_id):
    listing=Listing.objects.get(pk=listing_id)
    bid_count=listing.item.all().count()
    if request.method=="POST":
        form=CreateBid(request.POST)
        if form.is_valid():
            bid=float(request.POST['bid'])
            time=datetime.datetime.now()
            if bid_count==0:
                if bid>=listing.price:
                    listing.price=bid
                    listing.save()
                    bidder=request.user
                    listing.previous_bidder=request.user
                    listing.save()
                    bidding=Bidding(bidder=bidder,bid=bid,listing=listing)
                    bidding.save()
                    bid_count=listing.item.all().count()
                    return render(request,"auctions/listing.html",{
                        "content_bidding":CreateBid(),
                        "listing":listing,
                        "bid_count":bid_count,
                        "comments_of_this_listing":Comment.objects.filter(listing_commented=listing),
                        "user_watchlist":WatchList.objects.get(user=request.user)
                    })
                else:
                    return render(request,"auctions/listing.html",{
                        "content_bidding":form,
                        "listing":listing,
                        "bid_count":bid_count,
                        "error":f"The starting bid must be greater than ${listing.price}.",
                        "comments_of_this_listing":Comment.objects.filter(listing_commented=listing),
                        "user_watchlist":WatchList.objects.get(user=request.user)
                    }) 
            else:
                if bid>listing.price:
                    listing.price=bid
                    listing.save()
                    bidder=request.user
                    listing.previous_bidder=request.user
                    listing.save()
                    bidding=Bidding(bidder=bidder,bid=bid,listing=listing)
                    bidding.save()
                    bid_count=listing.item.all().count()
                    print(WatchList.objects.get(user=request.user))
                    return render(request,"auctions/listing.html",{
                        "content_bidding":CreateBid(),
                        "listing":listing,
                        "bid_count":bid_count,
                        "comments_of_this_listing":Comment.objects.filter(listing_commented=listing),
                        "user_watchlist":WatchList.objects.get(user=request.user)
                    })
                else:
                    return render(request,"auctions/listing.html",{
                        "content_bidding":form,
                        "listing":listing,
                        "bid_count":bid_count,
                        "error":f"The starting bid must be greater than ${listing.price}.",
                        "comments_of_this_listing":Comment.objects.filter(listing_commented=listing),
                        "user_watchlist":WatchList.objects.get(user=request.user)
                    }) 
    if request.user.is_authenticated:
        return render(request,"auctions/listing.html",{
            "content_bidding":CreateBid(),
            "listing":listing,
            "bid_count":bid_count,
            "comments_of_this_listing":Comment.objects.filter(listing_commented=listing),
            "user_watchlist":WatchList.objects.get(user=request.user)
        })
    else:
        return render(request,"auctions/listing.html",{
            "content_bidding":CreateBid(),
            "listing":listing,
            "bid_count":bid_count,
            "comments_of_this_listing":Comment.objects.filter(listing_commented=listing)
        })

def watchlist(request):
    if request.user.id!=None:
        user_watchlist=WatchList.objects.get(user=request.user)
    return render(request, "auctions/watchlist.html",{
        "user_watchlist":user_watchlist
    })

def close_listing(request,listing_id):
    listing=Listing.objects.get(pk=listing_id)
    if request.method=="POST":
        if request.user==listing.creator:
            listing.closed=True
            listing.save()
            return HttpResponseRedirect(reverse("listing",args=(listing.id,)))

def categories(request):
    return render(request,"auctions/categories.html",{
        "categories":Category.objects.all()
    })

def category(request,category):
    return render(request,"auctions/category.html",{
        "category_name":Category.objects.get(category=category)
    })
