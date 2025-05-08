from django.shortcuts import render , redirect , get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from Owner.models import Employee_Enrol
from Owner.forms import Employee_EditForm , Employee_EditForm1

# Create your views here.

def OwnerLogin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['pass']
        if (username == 'admin' and password == 'admin') or (username == 'owner' and password == 'owner'):
            return redirect('OwnerHome')
        else:
            return render(request, 'ownerlogin.html', {'error': 'Invalid username or password'})
    return render(request, 'ownerlogin.html')

def OwnerHome(request):
    return render(request, 'owner/OwnerHome.html')

def Emp_Register(request):
    if request.method == 'POST':
        Name = request.POST['name']
        username = request.POST['username']
        password = request.POST['pass']
        phone = request.POST['phone']
        email = request.POST['email']
        
        if User.objects.filter(username=username).exists():
            messages.info(request, 'Username already exists')
            return redirect('EmpRegister')
        elif Employee_Enrol.objects.filter(phone=phone).exists():
            messages.info(request, 'Phone number already exists')
            return redirect('EmpRegister')
        elif User.objects.filter(email=username).exists():
            messages.info(request, 'Email already exists')
            return redirect('EmpRegister')
        else:
            user = User.objects.create_user(username=username, password=password)
            user.save()
            if Name and phone:
                emp = Employee_Enrol.objects.create( name=Name, phone=phone , email=email,)
                emp.save()
            messages.info(request, 'Account created successfully')
            return redirect('EmpRegister')

        
    return render(request, 'owner/Empregister.html')





def Employee_View(request):
    data = User.objects.all()
    data1= Employee_Enrol.objects.all()

    return render(request, 'owner/EmployeeView.html' , {'combined': zip(data, data1)})

def Emp_Edit(request , id , employee_id):
     user  =get_object_or_404( User,id =id )
     employee=get_object_or_404(Employee_Enrol,id=employee_id )

     if request.method == 'POST':
        form = Employee_EditForm1(request.POST, instance=user)
        form1 = Employee_EditForm(request.POST, instance=employee)
        if form.is_valid() and form1.is_valid():
               user_instance = form.save(commit=False)
               if form.cleaned_data['password']:
                 user_instance.set_password(form.cleaned_data['password'])
               user_instance.save()
               form1.save()
            
               messages.success(request, 'Profile updated successfully')
               return redirect('Employeeview')
     else:
        form = Employee_EditForm1(instance=user)
        form1 = Employee_EditForm(instance=employee)
     return render(request, 'owner/EmployeeEdit.html', {'form': form, 'form1': form1})


def Emp_Delete(request , id , employee_id):
    user  = User.objects.filter(id =id )
    user1= Employee_Enrol.objects.filter(id = employee_id  )
    user.delete()
    user1.delete()
    return redirect('Employeeview')                                                                  
