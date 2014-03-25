#-*- encoding:utf-8 -*-
from django.shortcuts import render, render_to_response, get_object_or_404
from django.http import HttpResponseNotFound, HttpResponseForbidden, HttpResponse, HttpResponseRedirect
from models import Thread, Comment
from django.template import RequestContext
from models import *
from django.views.decorators.csrf import csrf_protect
from abstract.views import MessageBaseForm
import json
from django.core.urlresolvers import reverse


class EditKeyError(forms.ValidationError):
    def __init__(self):
        return forms.ValidationError.__init__(self, 'Inputted Edit Key is invalid')


class ThreadForm(MessageBaseForm):

    def clean_edit_key(self):
        base = self.data.get('edit_key', '')
        if self.instance:
            if self.instance.id and base:
                if self.instance.edit_key != base:
                    raise EditKeyError()
        return base

    class Meta(MessageBaseForm.Meta):
        model = Thread


class ThreadFormForAnon(ThreadForm):
    class Meta(ThreadForm.Meta):
        exclude = ('locked', ) + Thread.exclude()


class CommentForm(MessageBaseForm):

    def clean_edit_key(self):
        base = self.data.get('edit_key', '')
        if self.instance:
            if self.instance.id and base:
                if self.instance.edit_key != base:
                    raise EditKeyError()
        return base

    class Meta(MessageBaseForm.Meta):
        model = Comment
        exclude = MessageBaseForm.Meta.exclude + ('thread', )


# generic form in thread and comment
class DeleteForm(forms.Form):
    delete_key = forms.CharField(max_length=10, label="編集キー")

    def __init__(self, data={}, initial={}, instance=None):
        self.instance = instance
        return super(DeleteForm, self).__init__(data=data, initial=initial)

    def clean_delete_key(self):
        base = self.data.get('delete_key', '')
        if self.instance:
            if self.instance.id and base:
                if self.instance.edit_key != base:
                    raise EditKeyError()
        return base


def home(request):
    return render_to_response(
        'bbs/home.html',
        dict(
            threads=Thread.objects.all(),
        ),
        context_instance=RequestContext(request)
    )


@csrf_protect
def show_thread(request, thread_id):
    thread = get_object_or_404(Thread, pk = thread_id)
    if thread.locked:
        if not request.user.is_active:
            return HttpResponseRedirect('/auth/login?next=%s'%request.path)

    if request.POST:
        comment = Comment()
        comment.thread_id = thread_id
        comment_form = CommentForm(request.POST, instance=comment)
        v = comment_form.is_valid()
        if v:
            thread = comment_form.save()

        v_flag = request.GET.get('validation', None)
        if v_flag != 'true':
            if v:
                return HttpResponseRedirect(reverse('bbs.thread.show', args=(thread_id,)))
            else:
                context = request.POST
        else:
            content = dict(result=v, errors=comment_form.errors, redirect_to=reverse('bbs.thread.show', args=(thread_id,)))
            return HttpResponse(json.dumps(content), mimetype='text/plain')

    else:
        context = {}
        comment_form = CommentForm()

    return render(
        request,
        'bbs/show_thread.html',
        dict(
            thread=thread,
            comments=thread.comment_set.all(),
            comment_form=comment_form,
            delete_form=DeleteForm()
        ),
        context_instance=RequestContext(request, context)
    )


@csrf_protect
def edit_thread(request, thread_id=None):
    if not thread_id is None:
        thread = get_object_or_404(Thread, pk=thread_id)
        if thread.locked:
            if not request.user.is_active:
                return HttpResponseRedirect('/auth/login?next=%s' % request.path)
    else:
        thread = Thread()

    if request.user.is_active:
        tf = ThreadForm
    else:
        tf = ThreadFormForAnon

    if request.POST:
        thread_form = tf(request.POST, instance=thread)
        v = thread_form.is_valid()
        if v:
            thread = thread_form.save()

        v_flag = request.GET.get('validation', None)
        if v_flag != 'true':
            # ajaxでない
            if v:
                # validならリダイレクト
                return HttpResponseRedirect('/bbs/%s' % thread.id)
            else:
                # invalidなら下で処理
                context = request.POST
        else:
            # ajaxなときvalid,invalid問わず
            rt = '/bbs/%s' % thread.id
            content = dict(result=v, errors=thread_form.errors, redirect_to=rt)
            return HttpResponse(json.dumps(content), mimetype='text/plain')

    else:
        context = {}
        thread_form = tf(instance=thread, initial=dict(edit_key=''))

    return render_to_response('bbs/edit_thread.html',
                              dict(
                                  thread=thread,
                                  thread_form=thread_form,
                              ),
                              context_instance=RequestContext(request, context))

@csrf_protect
def delete_thread(request, thread_id):
    if request.POST:
        thread = get_object_or_404(Thread, pk=thread_id)
        form = DeleteForm(request.POST, instance=thread)
        v = form.is_valid()
        if v:
            thread.delete()

        v_flag = request.GET.get('validation', None)
        if v_flag == 'true':
            # ajaxなときvalid,invalid問わず
            content = dict(result=v, errors=form.errors, redirect_to='/bbs/')
            return HttpResponse(json.dumps(content), mimetype='text/plain')
        else:
            return HttpResponseForbidden()
    else:
        return HttpResponseForbidden()




@csrf_protect
def edit_comment(request, thread_id, comment_id=None):
    if comment_id:
        comment = get_object_or_404(Comment, pk=comment_id)
    else:
        comment = Comment()
        comment.thread_id = thread_id

    if request.POST:
        comment_form = CommentForm(request.POST, instance=comment)
        v = comment_form.is_valid()
        if v:
            comment_form.save()

        # validationがtrueならjsonで結果を返す
        v_flag = request.GET.get('validation', None)
        if v_flag != 'true':
            # ajaxでない
            if v:
                # validならリダイレクト
                return HttpResponseRedirect('/bbs/%s' % comment.thread_id )
            else:
                # invalidなら下で処理
                context = request.POST
        else:
            # ajaxなときvalid,invalid問わず
            content = dict(result=v, errors=comment_form.errors, redirect_to='/bbs/%s' % comment.thread_id);
            return HttpResponse(json.dumps(content), mimetype='text/plain')
    else:
        # postでないajaxでない(普通のアクセス)
        context = {}
        comment_form = CommentForm(instance=comment, initial=dict(edit_key=''))

    return render_to_response('bbs/edit_comment.html',
                              dict(
                                  comment=comment,
                                  comment_form=comment_form,
                              ),
                              context_instance=RequestContext(request, context))

@csrf_protect
def delete_comment(request, thread_id, comment_id):
    if request.POST:
        get_object_or_404(Thread, pk=thread_id)
        comment = get_object_or_404(Comment, pk=comment_id)
        form = DeleteForm(request.POST, instance=comment)
        v = form.is_valid()
        if v:
            comment.delete()

        v_flag = request.GET.get('validation', None)
        if v_flag == 'true':
            content = dict(result=v, errors=form.errors, redirect_to='/bbs/%s' % thread_id)
            return HttpResponse(json.dumps(content), mimetype='text/plain')
        else:
            return HttpResponseForbidden()
    else:
        return HttpResponseForbidden()



