from django.urls import path
from Owner import views

urlpatterns = [
    path('OwnerLogin', views.OwnerLogin , name ='OwnerLogin'),
    path('OwnerHome', views.OwnerHome , name ='OwnerHome'),
    path('EmpRegister', views.Emp_Register , name ='EmpRegister'),
    path('Employeeview', views.Employee_View , name ='Employeeview'),
    path('EmpployeeEdit/<int:id>/<str:employee_id>', views.Emp_Edit , name ='EmpployeeEdit'),
    path('Emp_delete/<int:id>/<str:employee_id>', views.Emp_Delete , name ='Emp_delete'),

]