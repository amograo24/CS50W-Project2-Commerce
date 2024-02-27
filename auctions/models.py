from django.contrib.auth.models import AbstractUser
from django.db import models
import datetime


class User(AbstractUser):
    pass


class Category(models.Model):
    category=models.CharField(max_length=60,default=None)    

    def __str__(self):
        return f"{self.category}"

class Listing(models.Model):
    
    item_name=models.CharField(max_length=100,default=None,verbose_name="Title")
    item_description=models.TextField(default=None,verbose_name="Description")
    image_url=models.URLField(default=None,verbose_name="Image URL",blank=True)
    price=models.FloatField(default=None,verbose_name="Price")
    item_category=models.ForeignKey(Category,on_delete=models.PROTECT,verbose_name="Item Category",related_name="listings",null=True,blank=True)
    date=models.DateTimeField(default=datetime.datetime.now())
    creator=models.ForeignKey(User,on_delete=models.CASCADE,related_name="creator")
    previous_bidder=models.ForeignKey(User,on_delete=models.CASCADE,related_name="previous_bidder",null=True)
    closed=models.BooleanField(default=False)

    def __str__(self):
        return f"{self.id}) {self.item_name}"

class Bidding(models.Model):
    time=models.DateTimeField(default=datetime.datetime.now())
    bid=models.FloatField()
    bidder=models.ForeignKey(User,on_delete=models.CASCADE)
    listing=models.ForeignKey(Listing,on_delete=models.CASCADE,default=None,related_name="item")

    def __str__(self):
        return f"{self.id}) ${self.bid} placed by {self.bidder} on '{self.listing.item_name}'"
    


class Comment(models.Model):
    time_of_comment=models.DateTimeField(default=datetime.datetime.now())
    comment=models.TextField(default=None,verbose_name="Comment")
    commenter=models.ForeignKey(User,on_delete=models.SET_NULL,related_name="commenter",null=True)
    listing_commented=models.ForeignKey(Listing,on_delete=models.CASCADE,default=None)

    def __str__(self):
        return f"{self.id}) {self.commenter} commented on '{self.listing_commented.item_name}'"

class WatchList(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE,related_name="user")
    listings=models.ManyToManyField(Listing,blank=True,related_name="listings")

    def __str__(self):
        return f"{self.user}'s watchlist"

