from django.shortcuts import render
from rest_framework import generics, permissions, mixins, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from .models import Post,Vote
from .serializers import PostSerializer, VoteSerializer
# Create your views here.

class PostListCreate(generics.ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer 
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self,serializer):
        serializer.save(poster = self.request.user)


class PostRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer 
    permission_classes = [permissions.IsAuthenticated]

    def perform_update(self,serializer):
        post = Post.objects.filter(pk = self.kwargs['pk'], poster=self.request.user)
        if post.exists():
            serializer.save()
        else:
            raise ValidationError('This is not your post to update')

    def get(self,request,*args,**kwargs):
        user = self.request.user
        if Post.objects.filter(poster=user,pk=self.kwargs['pk']):
            return self.retrieve(request,*args,**kwargs)
        else:
            raise ValidationError('This is not your post for a detailed view')

    def delete(self,request,*args,**kwargs):
        post = Post.objects.filter(pk = self.kwargs['pk'], poster=self.request.user)
        if post.exists():
            return self.destroy(request,*args, **kwargs)
        else:
            raise ValidationError('This is not your post to delete')



class VoteCreate(generics.CreateAPIView, mixins.DestroyModelMixin):
    serializer_class = VoteSerializer 
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        post = Post.objects.get(pk = self.kwargs['pk'])
        return Vote.objects.filter(voter = user, post = post)

    def perform_create(self,serializer):
        if self.get_queryset().exists():
            raise ValidationError('You have already voted to this post')
        else:
            serializer.save(voter = self.request.user, post = Post.objects.get(pk = self.kwargs['pk']))

    def delete(self,request,*args,**kwargs):
        if self.get_queryset().exists():
            self.get_queryset().delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            raise ValidationError('You have never voted this post')

