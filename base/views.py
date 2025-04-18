from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse
from .models import Room, Topic, Message, User
from .forms import RoomForm, UserForm
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout

# Create your views here.


# rooms = [
#     {'id': 1, 'name': 'Room 1', 'description': 'This is a room'},
#     {'id': 2, 'name': 'Room 2', 'description': 'This is another room'},
#     {'id': 3, 'name': 'Room 3', 'description': 'This is yet another room'},
#  ]


def LoginPage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')
        
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.error(request, 'User does not exist')  

        user = authenticate(request, username=username, password=password) 
        if user is not None:
            login(request, user)
            return redirect("home")     
        else:
            messages.error(request, 'User or password does not exist')

    context = {'page': page}
    return render(request, 'base/login_register.html', context)


def registerPage(request):
    form = UserCreationForm()
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'an error occurred during registraction')
    context = {'form': form}
    return render(request, 'base/login_register.html', context)


def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    feed_messages = Message.objects.filter(user=user)
    topics = Topic.objects.all()
    rooms_count = rooms.count()
    context = {'user': user, 'rooms': rooms,
    'feed_messages': feed_messages, 'rooms_count': rooms_count, 'topics':topics}
    return render(request, 'base/user_profile.html', context)


def logoutUser(request):
    logout(request)
    return redirect('home')


def home(request):
    q = request.GET.get('q') if request.GET.get('q') is not None else ''
    rooms = Room.objects.filter(
    Q(topic__name__icontains=q) |
    Q(name__icontains=q) |
    Q(host__username__icontains=q)
    )
    rooms_count = rooms.count()
    topics = Topic.objects.all()[:5]
    feed_messages = Message.objects.filter(Q(room__topic__name__icontains=q))
    context = {'rooms': rooms, 'topics': topics, 'rooms_count': rooms_count, 'feed_messages': feed_messages}
    return render(request, 'base/home.html', context)


def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all().order_by('-created')
    participants = room.participants.all()
    if request.method == 'POST':
        Message.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('room', pk=room.id)

    context = {'room': room, 'room_messages': room_messages, 'participants': participants}
    return render(request, 'base/room.html',  context)


@login_required(login_url="login")
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == 'POST':
        room_topic = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=room_topic)
        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description')
        )
        return redirect('home')
    context = {'form': form, 'topics': topics}
    return render(request, 'base/room_form.html', context)


@login_required(login_url='login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()

    if request.user != room.host:
        return HttpResponse('You are not allow here')
    if request.method == 'POST':
        room_topic = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=room_topic)
        room.topic = topic
        room.name = request.POST.get('name')
        room.description = request.POST.get('description')
        room.save()
        return redirect('home')
    context = {'form': form, 'topics': topics, 'room': room}
    return render(request, 'base/room_form.html', context)


@login_required(login_url="login")
def DeleteRoom(request, pk):
    room = Room.objects.get(id=pk)
    if request.user.id != room.host.id:
        return HttpResponse('You are not allow here')
    if request.method == 'POST':
        room.delete()
        return redirect('home')  # Redirect to the previous page
    context = {'obj': room}
    return render(request, 'base/delete.html', context)


@login_required(login_url="login")
def DeleteMessage(request, pk):
    message = Message.objects.get(id=pk)
    if request.user.id != message.user.id:
        return HttpResponse('You are not allow here')
    if request.method == 'POST':
        message.delete()
        return redirect('home')   # Redirect to the previous page
    context = {'obj': message.body}
    return render(request, 'base/delete.html', context)


login_required(login_url='login')
def updateUser(request):
    user = request.user
    userform = UserForm(instance=user)
    if request.method == 'POST':
        userform = UserForm(request.POST, instance=user)
        if userform.is_valid:
            userform.save()
            return redirect('user-profile', pk=user.id) 
        else:
            HttpResponse('something is worng in credentials')

    context = {'userform': userform}
    return render(request, 'base/update-user.html', context)


def allTopics(request):
    q = request.GET.get('q') if request.GET.get('q') is not None else ''

    topics = Topic.objects.filter(name__icontains=q)

    context = {'topics': topics}
    return render(request, 'base/topics.html', context)


def usersActivity(request):
    user_messages = Message.objects.all()
    return render(request, 'base/activity.html', {'user_messages': user_messages})    