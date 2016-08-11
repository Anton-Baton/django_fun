from __future__ import unicode_literals

from django.db import models
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User
from datetime import datetime


class Category(models.Model):
    name = models.CharField(max_length=128, unique=True)
    views = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)
    slug = models.SlugField()

    class Meta:
        verbose_name_plural = 'categories'

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):

        if self.views < 0:
            self.views = 0
        if self.likes < 0:
            self.likes = 0

        #if self.id is None:
        self.slug = slugify(self.name)

        super(Category, self).save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return self.name


class Page(models.Model):
    category = models.ForeignKey(Category)
    title = models.CharField(max_length=128)
    url = models.URLField()
    views = models.IntegerField(default=0)
    last_visit = models.DateTimeField(auto_now=True)
    first_visit = models.DateTimeField(auto_now=True)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        time = datetime.now()
        if not self.first_visit:
            # print '>>>> First visit\n'
            self.first_visit = time
        if not self.last_visit:
            # print '>>> Last visit\n'
            self.last_visit = time

        super(Page, self).save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return self.title


class UserProfile(models.Model):
    user = models.OneToOneField(User)

    website = models.URLField(blank=True)
    picture = models.ImageField(upload_to='profile_images', blank=True)

    def __str__(self):
        return self.user.username
