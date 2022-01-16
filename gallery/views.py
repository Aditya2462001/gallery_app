from subprocess import call
from django.contrib import auth
from django.http import request
from django.http.response import JsonResponse
from django.shortcuts import redirect, render 
from django.contrib.auth import login,logout,authenticate
from django.contrib.auth.models import User
from django.contrib import messages
from django.urls import resolvers
from .models import *
from django.template.loader import render_to_string
from django.contrib.auth import get_user_model
from django.core.mail import EmailMessage , send_mail
from django.conf import settings
from .form import *
from django.db.models import Q

import razorpay
from django.conf import settings


from django.urls import reverse

from django.utils.encoding import force_bytes, force_text , DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from django.views.decorators.csrf import csrf_exempt

from .utils import token_generator


razorpay_client = razorpay.Client(
    auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))



def index(request):
    like_count = []
    images = UploadImg.objects.all()
    categories = Category.objects.all()[:20]
    for l in images:
        get_like = like.objects.get(img = l)
        like_count.append({'like':len(get_like.authors.all()),'id':l.id})
        
    context = {
        'images':images,
        'categories':categories,
        'likes':like_count,
    }
    return render(request,'index.html',context)

def GetImage(request):
    author = None
    id = request.GET.get('id')
    image = UploadImg.objects.get(id = id)
    comments = Comment.objects.filter(uploadImg = image)
    replys = Reply.objects.filter(author = image.author)
    likes = like.objects.get(img = image)
    like_count = len(likes.authors.all())
    category = Category.objects.get(UploadImg = image)
    if request.user.is_active:
        author = Author.objects.get(user = request.user)
    context = {
        'image':image,
        'comments':comments,
        'replys':replys,
        'likes':like_count,
        'author':author,
        'category':category
    }
    data = render_to_string('image-model.html',context)
    return JsonResponse({'data':data})

def Contact(request):
    form = ContactForm()
    if request.method == 'POST':
       form = ContactForm(request.POST or None)
       print(form.errors)
       if form.is_valid():
           contact = form.save(commit=False)
           contact.save()
           form.save_m2m()
           messages.success(request,'')
    context = {
        'form':form,
    }
    return render(request,'contact.html',context)


def categories(request):
    categories = Category.objects.all()
    print(categories)
    context = {
        'categories':categories
    }
    return render(request,'category.html',context)

def categoryImg(request,slug):
    get_images = Category.objects.get(name = slug)
    all_images = get_images.UploadImg.all()
    print(all_images)
    like_count = []
    for l in all_images:
        get_like = like.objects.get(img = l)
        like_count.append({'like':len(get_like.authors.all()),'id':l.id})
    context ={
        'images':all_images,
        'likes':like_count,
        'name':slug
    }
    return render(request,'all_images.html',context)

def search(request):
    search_data = request.GET.get('search')
    like_count = []
    categories = None
    authors = None
    images = None
    print(search_data)
    if Category.objects.filter(Q(name__icontains = search_data)).exists():
        categories = Category.objects.filter(Q(name__icontains = search_data))
    
    if Author.objects.filter(Q(fname__icontains = search_data) | Q(lname__icontains = search_data)).exists():
        authors = Author.objects.filter(Q(fname__icontains = search_data) | Q(lname__icontains = search_data))
    
    if UploadImg.objects.filter(Q(title__icontains = search_data)).exists():
        images = UploadImg.objects.filter(Q(title__icontains = search_data))
        for l in images:
            get_like = like.objects.get(img = l)
            like_count.append({'like':len(get_like.authors.all()),'id':l.id})

    context = {
        'categories':categories,
        'authors':authors,
        'images':images,
        'likes':like_count
    }
    print(context)
    return render(request,'search.html',context)


def Feedbacks(request):
    feedbacks = Feedback.objects.all()
    context = {
        'feedbacks':feedbacks
    }
    return render(request,'feedbacks.html',context)

def About(request):

    donates = Donate.objects.all()

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        number = request.POST.get('number')
        amount = request.POST.get('amount')


        donate = Donate.objects.create(name = name,email = email,number = number,amount = amount)
        donate.save()

        currency = 'INR'

        razorpay_order = razorpay_client.order.create(dict(amount=int(amount)*100,currency=currency,payment_capture='0'))

        razorpay_orderId = razorpay_order['id']
        donate.razorpay_orderId = razorpay_order['id']
        donate.save()


        call_back_url = 'http://127.0.0.1:8000/handleRequest'


        context = {
            'name':name,
            'number':number,
            'email':email,
            'order_id':razorpay_orderId,
            'total_amount':amount * 100,
            'razor_payment_id':settings.RAZOR_KEY_ID,
            'callback_url':call_back_url,
            'currency':currency
        }

        return render(request,'makepayment.html',context)

    return render(request,'about.html',{'donates':donates})

@csrf_exempt
def HandleRequest(request):
    if request.method == 'POST':
        try:
            payment_id = request.POST.get('razorpay_payment_id', '')
            razorpay_order_id = request.POST.get('razorpay_order_id', '')
            signature = request.POST.get('razorpay_signature', '')
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }

            donate = Donate.objects.get(razorpay_orderId = razorpay_order_id)
            donate.razorpay_signature = signature
            donate.save()

            result = razorpay_client.utility.verify_payment_signature(params_dict)
            if result is None:
                amount = donate.amount*100  
                try:
                    razorpay_client.payment.capture(payment_id, amount)
                    donate.payment_status = 'SUCCESS'
                    donate.save()

                    messages.success(request,'Your Payment is Successful.')
                    return redirect('/about/')
                except:
                    donate.payment_status = 'FAIL'
                    donate.save()
                    messages.success(request,'Your Payment is FAIL.')
                    return redirect('/about/')
            else:
                donate.payment_status = 'FAIL'
                donate.save()
                messages.success(request,'Your Payment is FAIL.')
                return redirect('/about/')
        except:
            return redirect('/about/')
    else:
        return redirect('/about/')



def AuthorView(request):
    all_authors = Author.objects.all()
    context = {
        'authors':all_authors
    }
    return render(request,'authors.html',context)

def authorRelatedImg(request,pk,name):
    author_data = Author.objects.get(id = pk)
    images = UploadImg.objects.filter(author = author_data)
    like_count = []
    author_name = author_data.fname +" "+ author_data.lname
    for l in images:
        get_like = like.objects.get(img = l)
        like_count.append({'like':len(get_like.authors.all()),'id':l.id})
    context = {
        'images':images,
        'likes':like_count,
        'name':author_name
    }
    return render(request,'all_images.html',context)

@csrf_exempt
def Like(request):
    if request.user.is_active:
        get_author = Author.objects.get(user = request.user)
        if request.method == 'POST':
            id = request.POST.get('get_id')
            get_img = UploadImg.objects.get(id = id)

            if like.objects.filter(img = get_img ,authors = get_author).exists():
                data = 'you are already like this post'
                return JsonResponse({'data':data,'like':'no'})
            else:
                like_img = like.objects.get(img = get_img)
                like_img.authors.add(get_author)
                like_img.save()
                data = 'you liked poem!'
                return JsonResponse({'data':data,'like':len(like_img.authors.all())})
       
    else:
        return JsonResponse({'data':'you are not Logined in','like':'no'})

@csrf_exempt
def sendComment(request):
    content = None
    get_name = None
    print('get the value')
    if request.method == 'POST':
        content = request.POST.get('content')
        img_id =request.POST.get('img_id')
        if request.user.is_active:
            get_name = request.user.first_name + " "+request.user.last_name
        else:
            get_name = request.META.get('USERNAME')
            if len(get_name) == 0:
                get_name = request.META.get('USERDOMAIN')

        get_img = UploadImg.objects.get(id = img_id)
        set_comment = Comment(uploadImg = get_img , name = get_name,content = content)
        set_comment.save()
        print('comment is save')
        print(set_comment)

    return JsonResponse({'content':content,'name':get_name})

@csrf_exempt
def SendReply(request):
    if request.method == 'POST':
        comment_id = request.POST.get('comment_id')
        content = request.POST.get('reply_content')
        author_id = request.POST.get('author_id')

        author = Author.objects.get(id = author_id)
        get_comment = Comment.objects.get(id = comment_id)

        send_reply = Reply(comment = get_comment,author = author,content = content)
        send_reply.save()

        context = {
            'author_name':f'{send_reply.author.fname} {send_reply.author.lname}',
            'content':send_reply.content
        }

        return JsonResponse(context)
 



# ================ user authentication ============================================= #


def view_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username = username , password = password)

        if user is not None:
            if user.is_active:
                login(request,user)
                return redirect('/userpanal')
            else:
                messages.info(request,'Credintail are be wrong please try again!!')
                return render(request,'login.html')
        else:
             messages.info(request,'Credintail are be wrong please try again!!')
             return render(request,'login.html')
    return render(request,'login.html')




def view_register(request):
    if request.method == 'POST':
        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        email = request.POST.get('email')
        number = request.POST.get('number')
        city = request.POST.get('city')
        profession = request.POST.get('profession')
        desc = request.POST.get('desc')
        password = request.POST.get('password')
        password2 = request.POST.get('Vpassword')
        img = request.FILES.get('image')


        if password != password2:
            messages.info(request,"password not match!!! please try again")
            return render(request,'register.html',
                    {'fname':fname,
                    'lname':lname,
                    'email':email,
                    'number':number,
                    'city':city,
                    'profession':profession,
                    'desc':desc,})
        
        if User.objects.filter(username = email).exists():
            messages.info(request,'Username is exits please choose another one.')
            return render(request,'register.html',
                    {'fname':fname,
                    'lname':lname,
                    'email':email,
                    'number':number,
                    'city':city,
                    'profession':profession,
                    'desc':desc,
                    'username':email})

        user = User(first_name = fname,last_name = lname,email = email,username = email)
        user.set_password(password)
        user.is_active = False
        user.save()

        author = Author(user = user,
                        fname = fname , 
                        lname = lname , 
                        email = email , 
                        number = number,
                        city = city,
                        profession = profession ,
                        desc = desc)
        author.save()
        if img is not None:
            author.img = img
            author.save()
        
        # path_to_view

        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = token_generator.make_token(user)
        domain = get_current_site(request).domain

        link = reverse('activate',kwargs = {'uidb64':uidb64,'token':token})
        
        activate_url = 'http://'+domain+link

        email_body = f'hiii {fname} {lname},\n Please activate your account through this given link for exprloring the website \n {activate_url}'
        email_subject = 'Activate Your account'

        
        mail = EmailMessage(
        subject=email_subject,
        body=email_body,
        from_email=settings.EMAIL_HOST_USER,
        to=[email,]
        )
        mail.send()

        messages.info(request,'You have successfully Register your self')
        return render(request,'register.html')
    return render(request,'register.html')


def verificationEmail(request,uidb64,token):
    try:
        id = urlsafe_base64_decode(force_text(uidb64))
        user = User.objects.get(pk = id)

        if not token_generator.check_token(user,token):
            messages.info(request,'your account is activated please login and enjoy the experience of natura gallary ')
            return redirect('/login')

        if user.is_active:
            messages.info(request,'your account is activated please login and enjoy the experience of natura gallary ')
            return redirect('/login')
            
        user.is_active = True
        user.save()
        messages.success(request,'account activate successfully')
        return redirect('/login')

    except Exception as e:
        pass
    
    return redirect('/login')

    



def view_logout(request):
    if request.user.is_active:
        print("logout function")
        logout(request)
        return redirect('/')

    return redirect('/')


# =========================== user authentication end============================================= #


# ===================== userpanal ========================================== #

def userPanal(request):
    if request.user.is_active:
        author = Author.objects.get(user = request.user)
        images = UploadImg.objects.all()
        images = images.filter(author = author)
        context = {
            'images':images,
            'ImgCount':len(images),
            'author':author,
        }
        return render(request,'userpanal/userPanal.html',context)

    return redirect('login/')


def UserPanalSearch(request):
    if request.user.is_active:
        author = Author.objects.get(user = request.user)
        search = request.GET.get('search-inq')
        page = request.GET.get('page')
        images = None
        if len(page) == 0:
            images = UploadImg.objects.filter(Q(title = search) | Q(dsec = search))

        context = {
            'author':author,
            'images':images,
            'search':search,
            'ImgCount':len(images),
        }

        
        return render(request,'userpanal/userPanal.html',context)

    
    
    return redirect('/userpanal')



def editImg(request,pk):
    if request.user.is_active:
        author = Author.objects.get(user = request.user)

        context = {
            'author':author,
        }
        return render(request,'userpanal/userPanal.html',context)
    return redirect('login/')

def deleteImg(request,pk):
    if request.user.is_active:
        return render(request,'userpanal/userPanal.html')
    return redirect('login/')


def profile(request):
    if request.user.is_active:
        author = Author.objects.get(user = request.user)
        images = UploadImg.objects.all()
        images = images.filter(author = author)
        context = {
            'author':author,
            'images':len(images),
        }
        return render(request,'userpanal/Profile.html',context)
    return redirect('login/')

def editProfile(request):
    if request.user.is_active:
        author = Author.objects.get(user = request.user)
        if request.method == "POST":
            fname = request.POST.get('fname')
            lname = request.POST.get('lname')
            email = request.POST.get('email')
            number = request.POST.get('number')
            city = request.POST.get('city')
            profession = request.POST.get('profession')
            desc = request.POST.get('desc')
            username = request.POST.get('username')

            print(fname,lname,email,number,email,city,profession,desc,username)

            author.fname = fname
            author.lname = lname
            author.email = email
            author.number = number
            author.city = city
            author.profession = profession
            author.desc = desc

            author.save()

            user = User.objects.get(username = request.user.username)
            user.username = username
            user.save()

            print("Profile is successfully updated")

            return redirect('profile')

        print('edit profile function')

        context = {
            'author':author,
        }
        return render(request,'userpanal/edit_profile.html',context)
    return redirect('login/')

def EditProfileImg(request):
    if request.user.is_active:
        author = Author.objects.get(user = request.user)
        if request.method == "POST":
            image = request.FILES.get('image')
            if image is not None:
                author.img = image
                author.save()
                print("successful")

                return redirect('userpanal/profile')
        return redirect('userpanal/editProfile')

    return redirect('login/')

def uploadImg(request):
    if request.user.is_active:
        categories = Category.objects.all()
        author = Author.objects.get(user = request.user)
        if request.method == "POST":
            image = request.FILES.get('image')
            title = request.POST.get('title')
            desc = request.POST.get('desc')
            category_id = request.POST.get('category')

            upload_img = UploadImg(author = author,img = image , title = title,desc = desc)
            upload_img.save()

            set_cate = Category.objects.get(id = category_id)
            set_cate.UploadImg.add(upload_img)
            set_cate.save()

            set_like = like(img = upload_img)
            set_like.save()

            messages.info(request,'Added Image')

            return redirect('/userpanal')

        context = {
            'categories':categories,
            'author':author
        }
            
        return render(request,'userpanal/upload_img.html',context)
    return redirect('login/')


def comments(request):
    if request.user.is_active:
        author = Author.objects.get(user = request.user)
        images = UploadImg.objects.filter(author = author)
        comment_count = []
        for i in images:
            comments = Comment.objects.filter(uploadImg = i)
            comment_count.append({'count':len(comments),'id':i.id})
            
        print(comments)
        context = {
            'author':author,
            'images':images,
            'comments':comment_count
        }
        return render(request,'userpanal/comments.html',context)
    return redirect('login/')


def feedback(request):
    if request.user.is_active:
        author = Author.objects.get(user = request.user)
        if request.method == "POST":
            feedback = request.POST.get('feedback')
            rating = request.POST.get('rating')
            print(feedback)

            feed = Feedback(author = author,desc = feedback,rating = rating)
            feed.save()

            messages.info(request,"thank you for giving us the feedback..")
            return render(request,'userpanal/feedback.html')

        return render(request,'userpanal/feedback.html',{'author':author})
    return redirect('login/')


def reply(request):
    if request.user.is_active:
        return render(request,'userpanal/comments.html')
    return redirect('login/')


def EditUploadImage(request,pk):
    get_image = UploadImg.objects.get(id = pk)
    category = Category.objects.get(UploadImg=get_image)
    categories = Category.objects.all()
    if request.method == 'POST':
        image = request.FILES.get('image')
        title = request.POST.get('title')
        desc = request.POST.get('desc')
        category_id = request.POST.get('category')

        set_cate = Category.objects.get(id = category_id)
        if not Category.objects.filter(id = category_id,UploadImg=get_image).exists:
            set_cate.UploadImg.add(get_image)
            set_cate.save()

        get_image.image = image
        get_image.title = title
        get_image.desc = desc
        get_image.save()
        messages.success(request,'image data successfully updated')
        return redirect('/userpanal')

    context = {
        'image':get_image,
        'category':category,
        'categories':categories
    }
    return render(request,'userpanal/edit_img.html',context)

def DeleteUploadImage(request,pk):
    get_image = UploadImg.objects.get(id = pk)
    get_cate = Category.objects.get(UploadImg = get_image)
    get_cate.UploadImg.remove(get_image)
    get_cate.save()
    get_image.delete()
    messages.warning(request,'image deleted successfully')

    return redirect('/userpanal')




    



