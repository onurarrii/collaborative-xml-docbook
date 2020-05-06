"""collaborative_xml_docbook URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path

from docbook.views import IndexView, DocumentView, InsertChildView, SetNameView, DeleteElementByIdView, \
    DeleteElementAttributeView, SetElementAttributeView, SetElementTextView, InsertSiblingView, InsertTextView, \
    SaveView, DeleteView, LoadView, UploadView, GetJsonView

urlpatterns = [
    re_path(r'^$', IndexView.as_view(), name='index'),
    path('document/<str:document_id>/', DocumentView.as_view(), name='document_screen'),
    path('api/insert_child/<str:document_id>/', InsertChildView.as_view(), name='insert_child'),
    path('api/set_name/<str:document_id>/', SetNameView.as_view(), name='set_name'),
    path('api/delete_element_by_id/<str:document_id>/', DeleteElementByIdView.as_view(), name='delete_element_by_id'),
    path('api/delete_element_attribute/<str:document_id>/', DeleteElementAttributeView.as_view(), name='delete_element_attribute'),
    path('api/set_element_attr/<str:document_id>/', SetElementAttributeView.as_view(), name='set_element_attr'),
    path('api/set_element_text/<str:document_id>/', SetElementTextView.as_view(), name='set_element_text'),
    path('api/insert_sibling/<str:document_id>/', InsertSiblingView.as_view(), name='insert_sibling'),
    path('api/insert_text/<str:document_id>/', InsertTextView.as_view(), name='insert_text'),
    path('api/save/<str:document_id>/', SaveView.as_view(), name='save'),
    path('api/delete/<str:document_id>/', DeleteView.as_view(), name='delete'),
    path('api/load/<str:document_id>/', LoadView.as_view(), name='load'),
    path('api/upload/', UploadView.as_view(), name='upload'),
    path('api/get_document/json/<str:document_id>/', GetJsonView.as_view(), name='get_json')

]
