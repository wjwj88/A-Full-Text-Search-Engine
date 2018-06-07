from django.conf.urls import url
from django.contrib import admin
from elasticsearchapp.views import search
urlpatterns = [
    url(r'^admin/', admin.site.urls),
    #url(r'^$', QuestionList.as_view(), name='qa-list'),
    #url(r'^(?P<pk>\d+)/$', QuestionDetail.as_view(), name='qa-question'),
    url(r'^search/$', search, name='FS'),
]
