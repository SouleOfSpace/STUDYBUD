from django.db import models
# from django.contrib.auth.models import User, AbstractUser
from django.contrib.auth.models import AbstractUser

# Create your models here.

class User(AbstractUser):
    '''pass'''

    name = models.CharField(max_length=200, null=True)
    email = models.EmailField(unique=True, null=True)
    bio = models.TextField(null=True)

    avatar = models.ImageField(null=True, default='avatar.svg')

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

class Topic(models.Model):
    '''Пользователь постов'''
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class Room(models.Model):
    '''Пост'''
    host = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)        #Пользователь поста
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True)      #Раздел поста
    name = models.CharField(max_length=200)                                     #Имя поста
    description = models.TextField(null=True, blank=True)                       #Описание поста
    participants = models.ManyToManyField(
         User, related_name='participants', blank=True)                         #Пользователи оставившие комментарии
    updated = models.DateTimeField(auto_now=True)                               #Дата обновления
    created = models.DateTimeField(auto_now_add=True)                           #Дата создания

    class Meta:
        ordering = ['-updated', '-created']                                     #Сортировка по дате обновления и создания

    def __str__(self):
        return self.name

class Message(models.Model):
    '''Комментарии'''
    user = models.ForeignKey(User, on_delete=models.CASCADE)                    #Пользователь
    room = models.ForeignKey(Room, on_delete=models.CASCADE)                    #Пост к которуму пишут комментарий
    body = models.TextField()                                                   #Тело комментария
    updated = models.DateTimeField(auto_now=True)                               #Дата обновления
    created = models.DateTimeField(auto_now_add=True)                           #Дата создания

    class Meta:
        ordering = ['-updated', '-created']                                     #Сортировка по дате обновления и создания

    def __str__(self):
        return self.body[0:50]                                                  #Усекаем по длине комментарий
