from rest_framework import filters, permissions, viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from .models import Comment, Follow, Group, Post, User
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    CommentSerializer, FollowSerializer, GroupSerializer, PostSerializer)


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly,
    )

    def perform_create(self, serializer, *args, **kwargs):
        if serializer.is_valid():
            serializer.save(author=self.request.user)
        else:
            return Response(status=400)

    def get_queryset(self):
        queryset = Post.objects.all()
        group = self.request.query_params.get('group', None)
        if group is not None:
            queryset = Post.objects.filter(group=group)
        return queryset


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly
    )

    def perform_create(self, serializer, *args, **kwargs):
        if serializer.is_valid():
            serializer.save(author=self.request.user)
        else:
            return Response(status=400)

    def get_queryset(self):
        post_id = self.kwargs.get('post_id')
        post = get_object_or_404(Post, pk=post_id)
        all_comments_of_post = post.comments.all()
        return all_comments_of_post


class FollowViewSet(viewsets.ModelViewSet):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    permission_classes = (permissions.IsAuthenticated,)
    filter_backends = [filters.SearchFilter]
    search_fields = ['=user__username', '=following__username']

    def get_queryset(self):
        user = get_object_or_404(User, username=self.request.user)
        return Follow.objects.filter(following=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
