from django.urls import path

from StoreManager import views

urlpatterns = [
   path('StoreManagerLogin', views.StoreManager_Login , name ='StoreManagerLogin'),
   path('StoreManagerHome', views.StoreManagerHome , name ='StoreManagerHome'),
   path('UploadImage/', views.upload_image , name ='UploadImage'),

]