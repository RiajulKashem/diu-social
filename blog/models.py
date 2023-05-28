from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from ckeditor.fields import RichTextField

""" Post model """


class Post(models.Model):
    title = models.CharField(max_length=150)
    content = RichTextField(blank=True, null=True)
    date_posted = models.DateTimeField(default=timezone.now)
    featured_image = models.ImageField(
        upload_to='featured_image', blank=True, null=True
    )
    date_updated = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    likes = models.ManyToManyField(User, related_name="blogpost", blank=True)
    saves = models.ManyToManyField(User, related_name="blogsave", blank=True)

    def get_author(self):
        if self.author.first_name == '' and self.author.last_name == '':
            return self.author.username
        return self.author.first_name + ' ' + self.author.last_name

    def total_likes(self):
        return self.likes.count()

    def total_saves(self):
        return self.saves.count()

    def comment_list(self):
        return self.comments.filter(reply=None)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post-detail', kwargs={"pk": self.pk})


""" Comment model """


class Comment(models.Model):
    post = models.ForeignKey(
        Post, related_name="comments", on_delete=models.CASCADE
    )
    name = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.TextField(max_length=200)
    date_added = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(
        User, related_name="blogcomment", blank=True
    )
    reply = models.ForeignKey(
        'self', null=True, related_name="replies", on_delete=models.CASCADE
    )

    def get_author(self):
        if self.name.first_name == '' and self.name.last_name == '':
            return self.name.username
        return self.name.first_name + ' ' + self.name.last_name

    def total_clikes(self):
        return self.likes.count()

    def __str__(self):
        return '%s - %s - %s' % (self.post.title, self.name, self.id)

    def get_absolute_url(self):
        return reverse('post-detail', kwargs={"pk": self.pk})
