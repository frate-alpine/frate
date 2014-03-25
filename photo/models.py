#-*- encoding: utf-8 -*-

from django.db import models
from django import forms
# from django.conf import settings
from abstract.models import MessageBase
from django.core.files.storage import FileSystemStorage
from django_thumbs.db.models import ImageWithThumbsField
from member.models import Member
from django.db.models.signals import pre_save

from PIL import Image
import os


fs = FileSystemStorage()


class Album(MessageBase):
    author = models.ForeignKey(Member, blank=True, null=True, default=None)

    class Meta:
        verbose_name = verbose_name_plural = 'アルバム'

    def __unicode__(self):
        return self.title



class Photo(MessageBase):
    image = ImageWithThumbsField(upload_to='photo', storage=fs, sizes=((200, 200),) )
    author = models.ForeignKey(Member, related_name='author')
    member = models.ManyToManyField(Member, blank=True, related_name='member')
    album = models.ForeignKey(Album)

    class Meta:
        verbose_name = verbose_name_plural = '写真'

    def __unicode__(self):
        return self.title

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):

        if self.image and not os.path.exists(self.image.path):
            from cStringIO import StringIO

            self.image.open('r+b')

            a = self.image.read()
            im = Image.open(StringIO(a))
            # self.image.close()
            y = im.size[0] > im.size[1]
            if y:
                l = im.size[0]
                s = im.size[1]
            else:
                s = im.size[0]
                l = im.size[1]

            if l > 1920:
                a = 1920 * s / l
                im.thumbnail(y and (1920, a) or (a, 1920), Image.ANTIALIAS)
                print 'resize'

            fp = StringIO()
            im.save(fp, format=im.format)

            self.image.truncate(0)
            self.image.seek(0)
            self.image.write(fp.getvalue())

            # self.image.close()
            fp.close()

        r = super(Photo, self).save(force_insert, force_update, using, update_fields)
        return r




#pre_save.connect(pre_save_photo, sender=Photo)