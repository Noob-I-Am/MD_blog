from django.shortcuts import render, get_object_or_404
from django.http import Http404, HttpResponseBadRequest, JsonResponse, HttpResponse, HttpResponseForbidden
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from blog.models import Article, Category, Comment, Tag
from django.core import serializers
from django.core.serializers.python import Serializer
from django.core.paginator import Paginator
import os
from . import actions
from .form import ArticleCoverUploadForm
import time, json, markdown

from django.core.mail import send_mail
from django.conf import settings

# Create your views here.
def  show(request):
    subject = 'Thank you for registering to our site'
    message = ' it  means a world to us '
    email_from = settings.EMAIL_HOST_USER
    recipient_list = ['565223635@qq.com', ]
    send_mail(subject, message, email_from, recipient_list)
    return HttpResponse('已发送成功')


# 序列化api
def getBlog(request):
    blog_id = request.POST.get('blog_id')
    if blog_id is None or len(blog_id) == 0:
        raise Http404('id is invalid')
    blog = get_object_or_404(Article, pk=blog_id)
    result = {'blog': blog}
    mylist = []
    mylist.append(blog)
    s = serializers.serialize('json', mylist)
    print('type:', s)
    return JsonResponse(s, safe=False)


def get_categories(request):
    categories = Category.objects.all()
    data = []
    for i in categories:
        data.append({'pk':i.pk,'name':i.name})
    return JsonResponse(data, safe=False)

def article_edit_page(request, article_id):
    article = get_object_or_404(Article, pk=article_id)
    categories = Category.objects.all()
    tags = []
    for tag in article.tags.all():
        d = {'tag': tag.name}
        tags.append(d)
    if article.is_markdown:
        return render(request, 'blog/markdown_editor.html', locals())
    else:
        return render(request, 'blog/editor.html', locals())


def new_article(request, is_markdown):
    tags = []
    categories = Category.objects.all()
    if is_markdown:
        return render(request, 'blog/markdown_editor.html', locals())
    return render(request, 'blog/editor.html', locals())



def new_markdown_page(request):  # 新增post页面
    return render(request, 'blog/markdown_editor.html')



def save(request):
    post_data = request.POST
    article_id, title, summary, content, category, tags, is_markdown = \
        post_data.get('article_id'), \
        post_data.get('title'), \
        post_data.get('summary'), \
        post_data.get('content'), \
        post_data.get('category'), \
        post_data.get('tags'), \
        post_data.get('is_markdown'),

    cover = request.FILES.get('cover', None)
    upload_form = ArticleCoverUploadForm(request.POST, request.FILES)

    if article_id:
        article = get_object_or_404(Article, pk=int(article_id))
    else:
        article = Article()
        article.author = request.user
        article.updated_at = timezone.now()
    article.title, article.summary, article.content = title, summary, content
    article.created_at = timezone.now()
    if is_markdown == 'True':
        article.is_markdown = True
    elif is_markdown == 'False':
        article.is_markdown = False
    tag_list = []
    article.save()
    if tags:
        tag_list = actions.save_tags(tags)
    if category:
        category = Category.objects.get(pk=int(category))
        article.category = category
    previous_cover_path = ''
    if upload_form.is_valid() and cover:
        if article.cover:
            previous_cover_path = article.cover.path
        article.cover.save(cover.name, cover, save=False)
    article.tags.set(tag_list)
    if previous_cover_path:
        try:
            os.remove(previous_cover_path)
        except FileNotFoundError:
            pass
    article.save()
    return JsonResponse(serializers.serialize('python', [article]), safe=False)
    # return HttpResponse('save succeed')


##########################

def get_blog_list(page_size, page_number, conditions=None, orderings=None):
    if conditions:
        pass
        # conditions = json.loads(conditions)
    else:
        conditions = {}
    if orderings:
        pass
        # orderings = json.loads(orderings)
    else:
        orderings = ['-pk']
    query_set = Article.objects.filter(**conditions).order_by(*orderings)
    paginator = Paginator(query_set, page_size)
    blog_list = paginator.page(page_number)
    return blog_list


def search_for_blog(request):
    page_size, page_number = int(request.POST.get('pageSize') or 1), int(request.POST.get('pageNumber') or 1)
    conditions = request.POST.get('conditions')
    orderings = request.POST.get('orderings')
    return get_blog_list(page_size, page_number, conditions, orderings)


def index_page(request):  # 首页
    index_conditions = {
        'page_size': 6,
        'page_number': 1,
        'orderings': {'-updated_at'},
    }

    blog_list = get_blog_list(**index_conditions)
    return render(request, 'index.html', {'blog_list': blog_list})


# def detail_page(request, article_id):
#     # article_id = request.POST.get('article_id')
#     try:
#         article_id = int(article_id)
#     except TypeError as e:
#         return HttpResponseBadRequest('博客id错误')
#     article = get_object_or_404(Article, pk=article_id)
#     comments = actions.get_comments(article_id, page_size=10, page_index=1)
#     comment_list = []
#     for comment in comments:
#         nickname = comment.user.nickname
#         data = {'nickname': nickname, 'comment': comment}
#         comment_list.append(data)
#     return render(request, 'blog/detail.html', {'article': article, 'comments': comment_list})


def comment(request, article_id):
    if not request.user.is_authenticated:
        return HttpResponseForbidden('未登录');
    content = request.POST.get('content')
    article = get_object_or_404(Article, pk=article_id)
    comment = actions.leave_comment(article=article, user=request.user, content=content, )
    comment.save()
    data = {
        'topic_pk': comment.pk,
        'topic_user_nickname': comment.user.nickname,
        'topic_created_at': comment.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        'topic_content': comment.content
    }
    return JsonResponse(data)


def reply(request, comment_id):
    if comment_id:
        content = request.POST.get('content')
        reply_to = get_object_or_404(Comment, pk=comment_id)
        comment = actions.leave_reply(target_comment=reply_to, content=content, user=request.user)
        data = {
            'reply_user_nickname': comment.user.nickname,
            'reply_created_at': comment.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'reply_to_user_nickname': comment.reply_to_user.nickname,
            'reply_content': comment.content,
            'reply_pk': comment.pk,
        }
        return JsonResponse(data, safe=True)


def article_detail(request, article_id):
    article = get_object_or_404(Article, pk=article_id)
    tags = article.tags.all()
    category = article.category
    comment_data = []
    comments = actions.get_comments(article)
    for comment in comments:
        comment_dict = {}
        reply_list = actions.get_topic_reply(comment)
        comment_dict['topic'] = comment
        comment_dict['reply_list'] = reply_list
        comment_data.append(comment_dict)
    categories = Category.objects.all()
    article.views += 1
    article.save()
    data = {
        'article': article,
        'tags': tags,
        'category': category,
        'comment_data': comment_data,
        'comment_count': len(comment_data),
        'categories': categories
    }
    if article.is_markdown:
        marked = markdown.markdown(article.content)
        data['marked'] = marked
    return render(request, 'blog/article.html', data)
    # return render(request, 'blog/article.html', {
    #     'article': article,
    #     'tags': tags,
    #     'category': category,
    #     'comment_data': comment_data,
    #     'comment_count': len(comment_data)
    # })


def package_blog_list_data(count, object_list):
    package = {'count': count}
    data = []
    for item in object_list:
        article = dict()
        article['pk'] = item.pk
        if item.cover:
            article['cover'] = item.cover.url
        else:
            article['cover'] = ''
        article['title'] = item.title
        article['summary'] = item.summary
        article['author_name'] = item.author.nickname
        if item.author.avatar:
            article['author_avatar'] = item.author.avatar.url
        article['release_date'] = item.created_at.strftime('%Y-%m-%d %H:%M:%S')

        data.append(article)
    package['data'] = data
    return package
    # return {'message': 'hello'}


def blog_list_by_category(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    if request.method == 'POST':
        page_size = request.POST.get('page_size') or 10
        page_num = request.POST.get('page_num') or 1
        try:
            page_size = int(page_size)
            page_num = int(page_num)
        except ValueError as e:
            return HttpResponseBadRequest('分页参数不正确')
        all_article = Article.objects.filter(category=category).order_by('-created_at')
        paginator = Paginator(all_article, page_size)
        data = paginator.page(page_num).object_list
        response_data = package_blog_list_data(paginator.count, data)
        return HttpResponse(json.dumps(response_data, ensure_ascii=False))

    if request.method == 'GET':
        return render(request, 'blog/blogList.html', {
            'type': 'category',
            'type_name': '分类:'+category.name,
            'init_action': 'category',
            'param': category_id,
        })


def blog_list_by_tag(request, tag_id):
    tag = get_object_or_404(Tag, pk=tag_id)
    if request.method == 'POST':
        page_size = request.POST.get('page_size') or 10
        page_num = request.POST.get('page_num') or 1
        try:
            page_size = int(page_size)
            page_num = int(page_num)
        except ValueError as e:
            return HttpResponseBadRequest('分页参数不正确')

        all_article = Article.objects.filter(tags__pk=tag_id).order_by('-created_at')
        paginator = Paginator(all_article, page_size)
        data = paginator.page(page_num).object_list
        response_data = package_blog_list_data(paginator.count, data)
        return HttpResponse(json.dumps(response_data, ensure_ascii=False))
    if request.method == 'GET':
        return render(request, 'blog/blogList.html', {
            'type': 'tag',
            'type_name': '标签:'+tag.name,
            'init_action': 'tag',
            'param': tag_id
        })


def blog_list(request):
    if request.method == 'POST':
        page_size = request.POST.get('page_size') or 10
        page_num = request.POST.get('page_num') or 1
        try:
            page_size = int(page_size)
            page_num = int(page_num)
        except ValueError as e:
            return HttpResponseBadRequest('分页参数不正确')
        all_article = Article.objects.all().order_by('-created_at')
        paginator = Paginator(all_article, page_size)
        # data = paginator.page(page_num).object_list
        data = paginator.page(page_num).object_list
        response_data = package_blog_list_data(paginator.count, data)
        return HttpResponse(json.dumps(response_data, ensure_ascii=False))
        # return HttpResponse(serializers.serialize('json', data, fields=['pk', 'title', 'summary', 'cover']))

    if request.method == 'GET':
        return render(request, 'blog/blogList.html', {'type': 'all', 'type_name': '全部', 'init_action': 'all'})


def get_tags(request):
    tags = actions.get_used_tags()
    data = list()
    for tag in tags:
        data.append({
            'name': tag.name,
            'pk': tag.pk
        })
    return HttpResponse(json.dumps(data))
