from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth import login, logout, authenticate
from .forms import TodoForm
from .models import Todo
from django.utils import timezone
from django.contrib.auth.decorators import login_required


def home(request):
    return render(request, 'todo/home.html')

def signupuser(request):
    if request.method == "GET":
        return render(request, 'todo/signupuser.html', {'form': UserCreationForm()})
    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(request.POST['username'], password=request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('currenttodos')
            except IntegrityError:
                return render(request, 'todo/signupuser.html', {'form': UserCreationForm(), 'error': 'Username already exists'})

        else:
            return render(request, 'todo/signupuser.html', {'form': UserCreationForm(), 'error': 'Password did not match'})

def loginuser(request):
    if request.method == "GET":
        return render(request, 'todo/loginuser.html', {'form': AuthenticationForm()})
    else:
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'todo/loginuser.html', {'form': AuthenticationForm(), 'error': 'username and password did not match'})
        else:
            login(request, user)
            return redirect('currenttodos')

@login_required
def logoutuser(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')

@login_required
def currenttodos(request):
    todos = Todo.objects.filter(user=request.user, finished_at__isnull=True)
    return render(request, "todo/currenttodos.html", {'todos': todos})

@login_required
def todoview(request, todo_pk):
    todo_detail = get_object_or_404(Todo, pk=todo_pk, user=request.user)

    if request.method == 'GET':
        form = TodoForm(instance=todo_detail)
        return render(request, "todo/todo.html", {'todo': todo_detail, 'form': form})
    else:
        try:
            form = TodoForm(request.POST, instance=todo_detail)

            form.save()
            return redirect('currenttodos')
        except ValueError:
            return render(request, 'todo/createtodo.html', {'todo': todo_detail, 'form': form, 'error': 'Data Error. Try again'})

@login_required
def createtodo(request):
    if request.method == "GET":
        return render(request, 'todo/createtodo.html', {'form': TodoForm()})
    else:
        try:
            form = TodoForm(request.POST)
            new_todo = form.save(commit=False)
            new_todo.user = request.user
            new_todo.save()
            return redirect('home')
        except ValueError:
            return render(request, 'todo/createtodo.html', {'form': TodoForm(), 'error': 'Data Error. Try again'})

@login_required
def todofinished(request, todo_pk):
    todo_detail = get_object_or_404(Todo, pk=todo_pk, user=request.user)

    if request.method == 'POST':
        todo_detail.finished_at = timezone.now()
        todo_detail.save()
        return redirect('currenttodos')

@login_required
def tododeleted(request, todo_pk):
    todo_detail = get_object_or_404(Todo, pk=todo_pk, user=request.user)

    if request.method == 'POST':
        todo_detail.finished_at = timezone.now()
        todo_detail.delete()
        return redirect('currenttodos')

@login_required
def finishedtodos(request):
    todos = Todo.objects.filter(user=request.user, finished_at__isnull=False).order_by('-finished_at')
    return render(request, "todo/finishedtodos.html", {'todos': todos})