from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import DetailView
from .models import Post, Comment
from .forms import CommentForm

class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/post_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = self.object.comments.all()
        context['comment_form'] = CommentForm()
        return context

@login_required
def add_comment(request, pk):
    post = get_object_or_404(Post, pk=pk)
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            messages.success(request, 'Your comment has been added!')
            return redirect('post-detail', pk=post.pk)
    
    return redirect('post-detail', pk=post.pk)

@login_required
def edit_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    
    # Check if the current user is the author
    if comment.author != request.user:
        messages.error(request, 'You are not authorized to edit this comment.')
        return redirect('post-detail', pk=comment.post.pk)
    
    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your comment has been updated!')
            return redirect('post-detail', pk=comment.post.pk)
    else:
        form = CommentForm(instance=comment)
    
    return render(request, 'blog/edit_comment.html', {
        'form': form,
        'comment': comment
    })

@login_required
def delete_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    post_pk = comment.post.pk
    
    # Check if the current user is the author
    if comment.author != request.user:
        messages.error(request, 'You are not authorized to delete this comment.')
        return redirect('post-detail', pk=post_pk)
    
    if request.method == 'POST':
        comment.delete()
        messages.success(request, 'Your comment has been deleted!')
        return redirect('post-detail', pk=post_pk)
    
    return render(request, 'blog/delete_comment.html', {'comment': comment})
