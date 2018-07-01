from django.shortcuts import render,get_object_or_404 ,redirect,HttpResponseRedirect
from django.utils import timezone
from blog_app.models import Post, Comment
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django import forms
from django.views.generic import ( TemplateView,ListView,DetailView,CreateView,UpdateView,DeleteView )
from django.contrib.auth.mixins import LoginRequiredMixin
from blog_app.forms import PostForm,CommentForm,UserRegistrationForm
# Create your views here.

class AboutView(TemplateView):
    template_name='blog_app/about.html'

class PostListView(ListView):
    model= Post
    context_object_name='post_list'
    def get_queryset(self):
        return Post.objects.filter(published_date__lte=timezone.now()).order_by('-published_date')


class PostDetailView(DetailView):
    model=Post

class PostCreateView(LoginRequiredMixin,CreateView):
    login_url= '/login/'
    redirect_field_name='blog_app/post_detail.html'
    form_class= PostForm
    model=Post

class PostUpdateView(LoginRequiredMixin,UpdateView):
    login_url= '/login/'
    redirect_field_name='blog_app/post_detail.html'
    form_class= PostForm
    model=Post

class PostDeleteView(LoginRequiredMixin,DeleteView):
    model=Post
    success_url=reverse_lazy('blog_app:post_list')

class DraftListView(LoginRequiredMixin,ListView):
    login_url= '/login/'
    redirect_field_name='blog_app/post_list.html'
    model=Post
    context_object_name= 'posts'
    template_name='blog_app/post_draft_list.html'

    def get_queryset(self):
        return Post.objects.filter(published_date__isnull=True).order_by('create_date')

def userRegister(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            userObj = form.cleaned_data
            username = userObj['username']
            email =  userObj['email']
            password =  userObj['password']
            if not (User.objects.filter(username=username).exists() or User.objects.filter(email=email).exists()):
                User.objects.create_user(username, email, password)
                user = authenticate(username = username, password = password)
                login(request,user)
                return HttpResponseRedirect('/')
            else:
                raise forms.ValidationError('Looks like a username with that email or password already exists')


    else:
        form = UserRegistrationForm()
    # context={'hello':"hello"}
    return render(request,'blog_app/register.html',{'form':form})



@login_required
def post_publish(request,pk):
    post=get_object_or_404(Post,pk=pk)
    post.validtext()
    post.publish()
    return redirect('blog_app:post_list')


@login_required
def add_comment_to_post(request,pk):
    post= get_object_or_404(Post,pk=pk)
    if request.method== 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment= form.save(commit=False)
            comment.post=post
            comment.save()
            return redirect('blog_app:post_detail',pk=post.pk)
    else:
        form= CommentForm()
    return render(request,'blog_app/comment_form.html',{'form':form})

@login_required
def comment_approve(request,pk):
    comment = get_object_or_404(Comment,pk=pk)
    comment.approve()
    return redirect('blog_app:post_detail',pk=comment.post.pk)

@login_required
def comment_remove(request,pk):
    comment= get_object_or_404(Comment,pk=pk)
    post_pk= comment.post.pk
    comment.delete()
    return redirect('blog_app:post_detail',pk=post_pk)
