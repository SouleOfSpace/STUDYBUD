from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from .models import Room, Topic, Message, User
from .forms import RoomForm, UserForm, MyUserCreationForm


def loginPage(request):
    '''Страница входа'''

    page = 'login'

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        #Проверка на правильность и уникальность username
        try:
            user = User.objects.get(email=email)
        except:
            messages.error(request, 'User does not exist')

        #аунтификация поользователя
        user = authenticate(request, email=email, password=password)

        #Если user аунти-ся - возвращаемся на home page, если нет - остаемся на странице и получаем сообщение
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Username or password does exit')

    context = {'page': page}
    return render(request, 'base/login_register.html', context)

def logoutUser(request):
    '''Выход аунтифицированного пользователя'''

    logout(request)
    return redirect('home')

def registerPage(request):
    '''Регистрация пользователя'''

    form = MyUserCreationForm()

    if request.method == 'POST':
        form = MyUserCreationForm(request.POST, request.FILES)

        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)

            return redirect('home')
        else:
            messages.error(request, 'An error occurred during registration')


    return render(request, 'base/login_register.html', {'form': form})

def home(request):
    '''Обработчик домашней страницы'''

    #Получаем поисковое слово из метода GET
    q = request.GET.get('q') if request.GET.get('q') != None else ''

    #Ищем пост по поисковому слову, кторое является частью одного из полей class Room
    rooms = Room.objects.filter(Q(topic__name__icontains=q) |
                                Q(name__icontains=q) |
                                Q(description__icontains=q)
                                )

    topics = Topic.objects.all()[0:5]
    room_count = rooms.count()
    #Комментарии к данному посту
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))

    context = {'rooms': rooms, 'topics': topics,
               'room_count': room_count, 'room_messages': room_messages}
    return render(request, 'base/home.html', context)

def room(request, pk):
    '''Обработчик страницы поста'''

    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all().order_by('-created')
    participants = room.participants.all()  #Все пользователи оставлявшие комментарии

    #Если был отправлен POST запрос, то создаем комментарий и добавляем user-a, который оставил комментарий в поле поста
    if request.method == 'POST':
        message = Message.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get('body')
        )

        room.participants.add(request.user)

        return redirect('room', pk=room.id)

    context = {'room': room, 'room_messages': room_messages,
               'participants': participants}

    return render(request, 'base/room.html', context)

def userProfile(request, pk):
    '''Профиль пользователя'''

    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()

    context = {'user': user, 'rooms': rooms,
               'room_messages': room_messages, 'topics': topics}

    return  render(request, 'base/profile.html', context)

@login_required(login_url='login')
def createRoom(request):
    '''Обработчик создания поста'''

    form = RoomForm()
    topics = Topic.objects.all()

    #Проверка на наличия аунтифицированного пользователя
    if request.user == None:
        return HttpResponse("You are not allowed here!")

    #Создание поста
    if request.method == 'POST':
        # form = RoomForm(request.POST)
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description')
        )

        # if form.is_valid():
        #     room = form.save(commit=False)
        #     room.host = request.user
        #     room.save()

        return redirect('home')

    context = {'form': form, 'topics': topics}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def updateRoom(request, pk):
    '''Обоаботчик редактирования поста'''

    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()

    #Проверка на то, что создатель поста пытается редактировать свой же пост и никто другой
    if request.user != room.host:
        return HttpResponse("You are not allowed here!")

    #Редактирование поста
    if request.method == "POST":
        # form = RoomForm(request.POST, instance=room)
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)

        # if form.is_valid():
        #     form.save()
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()

        return redirect('home')

    context = {'form': form, 'topics': topics, 'room': room}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def deleteRoom(request, pk):
    '''Обработчик удаления поста'''

    room = Room.objects.get(id=pk)

    # Проверка на то, что создатель поста пытается удалить свой же пост и никто другой
    if request.user != room.host:
        return HttpResponse("You are not allowed here!")

    #Удаление поста
    if request.method == "POST":
        room.delete()
        return redirect('home')

    return render(request, 'base/delete.html', {'obj': room})


@login_required(login_url='login')
def deleteMessage(request, pk):
    '''Обработчик удаления комментария'''
    message = Message.objects.get(id=pk)

    # Проверка на то, что создатель поста пытается удалить свой же комментарий и никто другой
    if request.user != message.user:
        return HttpResponse("You are not allowed here!")

    # Удаление комментария
    if request.method == "POST":
        message.delete()
        return redirect('home')

    return render(request, 'base/delete.html', {'obj': message})

@login_required(login_url='login')
def updateUser(request):
    '''pass'''
    user = request.user
    form = UserForm(instance=user)

    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=user)
        print(request.FILES)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)

    context = {'form': form}
    return render(request, 'base/update-user.html', context)

def topicPage(request):
    '''pass'''

    q = request.GET.get('q') if request.GET.get('q') != None else ''
    topics = Topic.objects.filter(name__icontains=q)
    context = {'topics': topics ,'q': q}

    return render(request, 'base/topics.html', context)

def activityPage(request):
    '''pass'''
    room_messages = Message.objects.all()
    context = {'room_messages': room_messages }

    return render(request, 'base/activity.html', context)
