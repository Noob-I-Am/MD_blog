from django.urls import path
from . import views
from django.views.generic import TemplateView


app_name = 'blog'
urlpatterns = [
    ### pages
    path(r'save/', views.save),  # 保存编辑
    path(r'index/', views.index_page), # 首页
    path(r'editor/<int:article_id>', views.article_edit_page),
    # path(r'new_post/', views.new_markdown_page),
    path('detail/<int:article_id>/', views.article_detail),
    path(r'new_article/<int:is_markdown>', views.new_article),
    ###### api
    path('comment/<int:article_id>', views.comment),
    path('reply/<int:comment_id>', views.reply),
    path('get_categories/', views.get_categories),



    path('blog_list/', views.blog_list),
    path('tag/<int:tag_id>/', views.blog_list_by_tag),
    path('category/<int:category_id>/', views.blog_list_by_category),
    path('display_tags', views.get_tags),

    path('show/', views.show),




]

