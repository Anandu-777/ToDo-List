from django.shortcuts import render,redirect
from django.views.generic import View
from todoapp.models import Todo
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.utils.decorators import method_decorator
from django.contrib import messages



# Create your views here.

def signin_required(fn):
    def wrapper(request, *args, **kwargs):
        
        if not request.user.is_authenticated:
            messages.error(request,"invalid session")
            return redirect("signin")
        else:
            return fn(request, *args, **kwargs)
    return wrapper



class RegistrationForm(forms.ModelForm):
    class Meta:
        model=User
        fields=["username","email","password"]
        widgets={
            "username": forms.TextInput(attrs={"class":"form-control"}),
            "email": forms.EmailInput(attrs={"class":"form-control"}),
            "password": forms.PasswordInput(attrs={"class":"form-control"}),
        
        }


class TodoForm(forms.ModelForm):
    class Meta:
        model=Todo
        exclude=("created_date","user_object",)
        widgets={
            "title":forms.TextInput(attrs={"class":"form-control"}),
            "status":forms.Select(attrs={"class":"form-control form-select"}),
        }


class LoginForm(forms.Form):
    username=forms.CharField(widget=forms.TextInput(attrs={"class":"form-control"}))
    password=forms.CharField(widget=forms.PasswordInput(attrs={"class":"form-control"}))

        
        
# signup
class SignUpView(View):
    def get(self, request, *args, **kwargs):
        form= RegistrationForm()
        return render(request,"register.html",{"form": form})
    
    def post(self, request, *args, **kwargs):
        form= RegistrationForm(request.POST)
        if form.is_valid():
            User.objects.create_user(**form.cleaned_data)
            print("created")
            return redirect("signin")
        else:
            print("failed")
            return render(request,"register.html",{"form": form})        
        
        
        
        
# VIEW   : FOR SIGNIN
# url    : localhost:8000/signin/
# method : get , post

class SignInView(View):
    def get(self,request,*args,**kwargs):
        form=LoginForm()
        return render(request,"login.html",{"form":form})

    def post(self,request,*args,**kwargs):
        form=LoginForm(request.POST)
        if form.is_valid():
            u_name=form.cleaned_data.get("username")
            pwd=form.cleaned_data.get("password")
            #  cheack valid or invalid
            user_object=authenticate(request,username=u_name,password=pwd)
            if user_object:
                print("credentials are valid")
                login(request,user_object)  # to start session   
                return redirect("todo-list")
        print("invalid")
        return render(request,"login.html",{"form":form})


@method_decorator(signin_required,name="dispatch")
class SignOutView(View):
    def get(self,request,*args,**kwargs):
        logout(request)
        return redirect("signin")

        

# view for listing all todo lists
# url:localhost:8000/todo/all/
# method:get
@method_decorator(signin_required,name="dispatch")
class TodoListView(View):
    def get(self, request, *args, **kwargs):
        qs=Todo.objects.filter(user_object=request.user)
        return render(request, 'todo_list.html',{"data":qs})
    
# view for creating a new todo
# url:localhost:8000/todo/add/
# method:get,post    
@method_decorator(signin_required,name="dispatch")
class TodoCreateView(View):
    def get(self, request, *args, **kwargs):
        form=TodoForm()
        return render(request, 'todo_add.html',{"form":form})
    def post(self, request, *args, **kwargs):
        form=TodoForm(request.POST)
        if form.is_valid():
            # form.save()
            data=form.cleaned_data
            Todo.objects.create(**data,user_object=request.user)
            return redirect ("todo-list")
        else:
            return render(request, "todo_add.html",{"form":form})

# todo detail view
# localhost:8000/todo/id/
# method get
@method_decorator(signin_required,name="dispatch")
class TodoDetailView(View):
    def get(self, request, *args,**kwargs):
        id=kwargs.get('pk')
        qs=Todo.objects.get(id=id)
        return render(request,'todo_details.html',{'data':qs})

@method_decorator(signin_required,name="dispatch")
class TodoDeleteView(View):
    def get(self, request, *args, **kwargs):
        id=kwargs.get('pk')
        Todo.objects.get(id=id).delete()
        return redirect('todo-list')

@method_decorator(signin_required,name="dispatch")
class TodoUpdateView(View):
    def get(self, request, *args, **kwargs):
        id=kwargs.get('pk')
        todo_object=Todo.objects.get(id=id)
        form=TodoForm(instance=todo_object)
        return render(request,'todo_edit.html',{'form':form})
    
    
    def post(self, request,*args,**kwargs):
        id=kwargs.get('pk')
        todo_object=Todo.objects.get(id=id)
        form=TodoForm(request.POST,instance=todo_object)
        if form.is_valid():
            form.save()
            return redirect('todo-list')
        else:
            return render(request, 'todo_list.html',{'form':form})
