from pyexpat import model
from django.db import models
from django.contrib.auth.models import User
from django.db.models import base

# Create your models here.

class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    fname = models.CharField( max_length=100)
    lname = models.CharField( max_length=100)
    email = models.EmailField(max_length=254)
    number = models.CharField(max_length=12)
    city = models.CharField(max_length=100)
    profession  = models.CharField( max_length=100,null=True,blank=True)
    desc = models.TextField()
    img = models.ImageField(upload_to='user_img',null = True , blank = True)

    def __str__(self):
        return self.fname

class UploadImg(models.Model):
    author = models.ForeignKey(Author,on_delete=models.CASCADE)
    img = models.ImageField(upload_to = 'upload_photo')
    title = models.CharField(max_length=50 ,null =True ,blank=True)
    desc = models.CharField(max_length=500 ,null =True , blank=True)

    def __str__(self):
        return self.title


class Category(models.Model):
    UploadImg = models.ManyToManyField(UploadImg,blank=True)
    name = models.CharField(max_length=100)
    cate_img = models.ImageField(upload_to='category-img', null=True)

    def __str__(self):
        return self.name


class Comment(models.Model):
    uploadImg = models.ForeignKey(UploadImg, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    content = models.CharField( max_length=2000)

    def __str__(self):
        return self.name
    
class Reply(models.Model):
    comment = models.ForeignKey(Comment,on_delete=models.CASCADE)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    content = models.CharField(max_length=1000)

    def __str__(self):
        return str(self.author)
    


class like(models.Model):
    img = models.ForeignKey(UploadImg,on_delete=models.CASCADE)
    authors = models.ManyToManyField(Author,blank= True)

    def __str__(self):
        return str(self.img.title)
    

class Feedback(models.Model):
    author = models.ForeignKey(Author,on_delete=models.CASCADE)
    rating = models.IntegerField(default=1)
    desc = models.TextField()

    def __str__(self):
        return str(self.author)

class ContactMe(models.Model):
    name = models.CharField(max_length=500,null=True,blank=True)
    email = models.EmailField(max_length=500,null=True,blank=True)
    number = models.CharField(max_length=500,null=True,blank=True)
    message = models.TextField()

    def __str__(self):
        return self.name


class Donate(models.Model):
    name = models.CharField(max_length=1000)
    email = models.EmailField(max_length=254)
    number = models.CharField(max_length=50)
    amount = models.IntegerField(default=0)
    payment_status = models.CharField(max_length=500,null=True,blank=True)

    razorpay_orderId = models.CharField(max_length=10000,null=True,blank=True)
    razorpay_signature = models.CharField(max_length=1000,null=True,blank=True)

    def __str__(self):
        return self.name
    

    
    
    

    
    

