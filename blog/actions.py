from .models import Comment, Category, Article, Tag
from user.models import User
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from django.utils.timezone import timezone
from django.conf import settings


def leave_comment(article, user, content):
    comment = Comment.objects.create(article=article, user=user, content=content, reply_to=None, reply_to_user=None, is_reply=False)
    comment.topic = comment
    comment.save()
    return comment


def leave_reply(target_comment, content, user):
    reply = Comment(
        user=user,
        article=target_comment.article,
        content=content,
        reply_to=target_comment,
        reply_to_user=target_comment.user,
        topic=target_comment.topic
    )
    reply.save()
    return reply


def get_comments(article, page_size=10, page_index=1):
    result = Comment.objects.filter(article=article, reply_to=None, is_reply=False).order_by('-created_at')
    paginator = Paginator(result, page_size)
    list = paginator.page(page_index).object_list
    return list

def get_topic_reply(topic_comment, page_size=10, page_index=1):
    result = Comment.objects.filter(topic=topic_comment, is_reply=True).order_by('-created_at')
    paginator = Paginator(result, page_size)
    list = paginator.page(page_index).object_list
    return list

def get_reply(target_comment, page_size=10, page_index=1):
    result = Comment.objects.filter(Q(reply_to=target_comment)).order_by('-created_at')
    paginator = Paginator(result, page_size)
    list = paginator.page(page_index).object_list
    return list


def deactivate_comment(target_id):
    comment = get_object_or_404(Comment, pk=target_id)
    comment.is_active = False
    comment.save()
    return comment


def get_all_category():
    categories = Category.objects.all()
    return categories


def get_top5_tags():
    result = Tag.objects.all().order_by('-count')
    paginator = Paginator(result, per_page=5)
    tags = paginator.page(1)
    return tags


def get_used_tags():
    tags = Tag.objects.all()
    used_tags = list()
    for tag in tags:
        if tag.article_set.all().count() > 0:
            used_tags.append(tag)
    return used_tags


def save_tags(tags_str):      # 设置标签

    tag_name_list = tags_str.split(',')
    tag_list = []
    for name in tag_name_list:
        try:
            tag = Tag.objects.get(name__iexact=name)
        except ObjectDoesNotExist as e:
            tag = Tag.objects.create(name=name)
            tag.save()
        tag_list.append(tag)
    return tag_list


def get_tags_names(article_id):

    '''

    :param article_id: 博客Id
    :return: 标签名列表
    '''

    article = Article.objects.get(pk=article_id)
    tags = article.tags
    tags_names = []
    for item in tags:
        if item.is_active:
            tags_names.append(item.name)
    return tags_names


def get_blogs_by_tag(tag_id):
    tag = Tag.objects.get(pk=int(tag_id))
    articles = []
    if tag is not None and tag.is_active:
        articles = tag.article_set.all()
    return articles


def get_blogs_by_category(category_id):
    category = Category.objects.filter(pk=int(category_id))
    blog_list = Article.objects.filter(category=category)
    return blog_list

