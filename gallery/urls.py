from django.urls import path
from django.urls.conf import include
from . import views

urlpatterns = [
    path('',views.index,name='home'),
    path('get-image/',views.GetImage,name="getImage"),
    path('contact/',views.Contact,name="Contact"),
    path('feedbacks/',views.Feedbacks,name="Feedbacks"),
    path('about/',views.About,name="About"),
    path('handleRequest',views.HandleRequest,name="handle-request"),
    path('category/',views.categories,name="Categories"),
    path('category-img/<str:slug>',views.categoryImg,name="categoryImg"),
    path('search/',views.search,name="search"),
    path('authors/',views.AuthorView,name="authors"),
    path('author-images/<str:pk>/<str:name>',views.authorRelatedImg,name="authors-images"),
    path('comment/',views.sendComment,name="send_comment"),
    path('reply/',views.SendReply,name="send_reply"),
    path('like/',views.Like,name="like"),

    path('login/',views.view_login,name="login"),
    path('register/' , views.view_register , name="register"),
    path('activate/<uidb64>/<token>',views.verificationEmail,name="activate"),
    path('logout/',views.view_logout,name='logout'),

    path('userpanal/',views.userPanal,name='user_panal'),
    path('search-user-panal/',views.UserPanalSearch,name='UserPanalSearch'),
    path('userpanal/profile',views.profile , name ="profile"),
    path('userpanal/editProfile',views.editProfile,name="EditProfile"),
    path('userpanal/editProfileImg',views.EditProfileImg,name="EditProfileImg"),
    path('userpanal/uploadImg',views.uploadImg,name="uploadImg"),
    path('userpanal/comments',views.comments,name="comments"),
    path('userpanal/feedback',views.feedback,name="feedback"),
    path('delete-img/<str:pk>',views.DeleteUploadImage,name="DeleteUploadImage"),
    path('edit-image/<str:pk>',views.EditUploadImage,name="EditUploadImage"),

    path('categories/',views.categories,name='categories'),
]
