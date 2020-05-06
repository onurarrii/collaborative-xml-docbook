import json

from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views import View

from docbook.dbd.DBDPersistency import DBDPersistency
from docbook.forms import InsertChildForm, DeleteElementByIdForm, InsertTextForm, InsertSiblingForm, SetElementTextForm, \
    SetElementAttributeForm, DeleteElementAttributeForm, SetNameForm, SaveForm, UploadForm
from docbook.globals.SharedVariables import SharedVariables
from docbook.util import SocketUtil


def parse_xml_to_json(xml_content, json_response={}):
    children = xml_content.getchildren()

    if "page" in xml_content.tag:
        page_tag = "page xmlns=\"http://projectmallard.org/1.0/\" "
        for attr, value in xml_content.attrib.items():
            page_tag += (" {}= \"{}\"").format(attr, value)
            if attr == 'id':
                json_response['id'] = value
        json_response['label'] = page_tag
        json_response['children'] = []


    elif not children:
        child_tag = xml_content.tag
        if "{http://projectmallard.org/1.0/}" in child_tag:
            child_tag = child_tag.replace("{http://projectmallard.org/1.0/}", "")
        child_attr = xml_content.attrib
        for attr, value in child_attr.items():
            child_tag += (" {}= \"{}\"").format(attr, value)
            if attr == 'id':
                json_response['id'] = value

        json_response['label'] = child_tag
        json_response["children"] = []
        if xml_content.text:
            json_response["children"].append({'label': xml_content.text})
        return json_response

    if children:
        for child in children:

            child_label = child.tag
            if "http://projectmallard.org/1.0/" in child_label:
                child_label = child_label.replace("{http://projectmallard.org/1.0/}", "")
            child_attr = child.attrib
            for attr, value in child_attr.items():
                child_label += (" {}= \"{}\"").format(attr, value)
                if attr == 'id':
                    child_id = value
            json_response['children'].append(
                parse_xml_to_json(child, {'id': child_id, 'label': child_label, "children": []}))
            if child.tail and '\n' not in child.tail:
                json_response['children'].append({'label': child.tail})
    return json_response


class IndexView(View):
    def get_dbdoc_list(self):
        documents = DBDPersistency.list()
        dirty_documents = [doc[1] for doc in DBDPersistency.listmem(True)]
        id_list = [i.get_id() for i in dirty_documents]
        clean_documents = []

        ''' eliminate duplicate documents for better displaying '''
        for doc in documents:
            if doc.get_id() not in id_list:
                clean_documents.append(doc)

        return dirty_documents, clean_documents

    def get(self, request):
        if not request.session.exists(request.session.session_key):
            request.session.create()
        form_upload = UploadForm()
        dirty_documents, clean_documents = self.get_dbdoc_list()

        return render(request, 'docbook/index.html',
                      {'dirty_documents': dirty_documents, 'clean_documents': clean_documents,
                       'form_upload': form_upload})

    def post(self, request):  # Create new document
        try:
            session_key = request.session.session_key
            dbd_controller = SharedVariables.add_dbd_controller(session_key, 'NEW')
            dbdoc_id = dbd_controller.get_id()
            return HttpResponseRedirect('/document/{}'.format(dbdoc_id))
        except Exception as e:
            return render(request, 'docbook/index.html', {'error': str(e), 'documents': self.get_dbdoc_list()})


class DocumentView(View):
    def get(self, request, **kwargs):
        if not request.session.exists(request.session.session_key):
            return HttpResponseRedirect('/')
        session_key = request.session.session_key
        dbdoc_id = kwargs['document_id']
        dbd_controller = SharedVariables.get_dbd_controller(session_key, dbdoc_id)

        if dbd_controller is None:
            request.session['error'] = None
            return HttpResponseRedirect('/')

        dbdoc = dbd_controller.dbdoc
        xml_content = str(dbdoc)
        form_insert_child = InsertChildForm()
        form_delete_element_by_id = DeleteElementByIdForm()
        form_set_name = SetNameForm()
        form_delete_element_attribute = DeleteElementAttributeForm()
        form_set_element_attr = SetElementAttributeForm()
        form_set_element_text = SetElementTextForm()
        form_insert_sibling = InsertSiblingForm()
        form_insert_text = InsertTextForm()
        form_save = SaveForm()
        form_upload = UploadForm()
        doc_name = dbdoc.get_name()

        try:
            error = request.session['error']
        except KeyError:
            error = None
        request.session['error'] = None

        return render(request, 'docbook/document.html',
                      {'doc_name': doc_name, 'form_upload': form_upload,
                       'form_save': form_save, 'xml_content': xml_content, 'form_insert_child': form_insert_child,
                       'form_delete_element_by_id': form_delete_element_by_id, 'dbdoc_id': dbdoc.get_id(),
                       'form_set_name': form_set_name, 'form_delete_element_attribute': form_delete_element_attribute,
                       'form_set_element_attr': form_set_element_attr, 'form_set_element_text': form_set_element_text,
                       'form_insert_sibling': form_insert_sibling, 'form_insert_text': form_insert_text,
                       'error': error, 'session_key': session_key})

    def post(self, request, **kwargs):
        if not request.session.exists(request.session.session_key):
            return HttpResponseRedirect('/')
        session_key = request.session.session_key
        dbd_controller = SharedVariables.add_dbd_controller(session_key, kwargs['document_id'])
        dbdoc = dbd_controller.dbdoc
        xml_content = str(dbdoc)

        form_insert_child = InsertChildForm()
        form_delete_element_by_id = DeleteElementByIdForm()
        form_set_name = SetNameForm()
        form_delete_element_attribute = DeleteElementAttributeForm()
        form_set_element_attr = SetElementAttributeForm()
        form_set_element_text = SetElementTextForm()
        form_insert_sibling = InsertSiblingForm()
        form_insert_text = InsertTextForm()
        form_save = SaveForm()
        form_upload = UploadForm()
        doc_name = dbdoc.get_name()
        return render(request, 'docbook/document.html',
                      {'doc_name': doc_name, 'xml_content': xml_content, 'form_upload': form_upload,
                       'form_save': form_save, 'form_insert_child': form_insert_child,
                       'form_delete_element_by_id': form_delete_element_by_id, 'dbdoc_id': dbdoc.get_id(),
                       'form_set_name': form_set_name, 'form_delete_element_attribute': form_delete_element_attribute,
                       'form_set_element_attr': form_set_element_attr, 'form_set_element_text': form_set_element_text,
                       'form_insert_sibling': form_insert_sibling, 'form_insert_text': form_insert_text,
                       'session_key': session_key})


class InsertChildView(View):
    def post(self, request, **kwargs):
        session_key = request.session.session_key
        form = InsertChildForm(request.POST)
        dbdoc_id = kwargs['document_id']
        controller = SharedVariables.get_dbd_controller(session_key, dbdoc_id)
        if form.is_valid():
            try:
                id = form.cleaned_data['id']
                tag = form.cleaned_data['tag']
                append = form.cleaned_data['append']
                result, message = controller.insert_child(id, tag, append)
            except Exception as e:
                request.session['error'] = str(e)
                SocketUtil.notify(dbdoc_id, session_key=session_key, error=str(e))
                return HttpResponse()
            if result is None:
                request.session['error'] = str(message)
                SocketUtil.notify(dbdoc_id, session_key=session_key, error=str(message))
            return HttpResponse()

    def get(self, request, **kwargs):
        return HttpResponseRedirect('/')


class SetNameView(View):
    def post(self, request, **kwargs):
        session_key = request.session.session_key
        form = SetNameForm(request.POST)
        dbdoc_id = kwargs['document_id']
        controller = SharedVariables.get_dbd_controller(session_key, dbdoc_id)
        if form.is_valid():
            try:
                name = form.cleaned_data['name']
                result, message = controller.set_name(name)
            except Exception as e:
                request.session['error'] = str(e)
                SocketUtil.notify(dbdoc_id, session_key=session_key, error=str(e))
                return HttpResponse()
            if result is False:
                request.session['error'] = str(message)
                SocketUtil.notify(dbdoc_id, session_key=session_key, error=str(message))
            return HttpResponse()

    def get(self, request, **kwargs):
        return HttpResponseRedirect('/')


class DeleteElementByIdView(View):
    def post(self, request, **kwargs):
        session_key = request.session.session_key
        form = DeleteElementByIdForm(request.POST)
        dbdoc_id = kwargs['document_id']
        controller = SharedVariables.get_dbd_controller(session_key, dbdoc_id)
        if form.is_valid():
            try:
                id = form.cleaned_data['id']
                result, message = controller.delete_element_by_id(id)
            except Exception as e:
                request.session['error'] = str(e)
                SocketUtil.notify(dbdoc_id, session_key=session_key, error=str(e))
                return HttpResponse()
            if result is False:
                request.session['error'] = str(message)
                SocketUtil.notify(dbdoc_id, session_key=session_key, error=str(message))
            return HttpResponse()

    def get(self, request, **kwargs):
        return HttpResponseRedirect('/')


class DeleteElementAttributeView(View):
    def post(self, request, **kwargs):
        session_key = request.session.session_key
        form = DeleteElementAttributeForm(request.POST)
        dbdoc_id = kwargs['document_id']
        controller = SharedVariables.get_dbd_controller(session_key, dbdoc_id)
        if form.is_valid():
            try:
                id = form.cleaned_data['id']
                attribute = form.cleaned_data['attribute']
                result, message = controller.delete_element_attr(id, attribute)
            except Exception as e:
                request.session['error'] = str(e)
                SocketUtil.notify(dbdoc_id, session_key=session_key, error=str(e))
                return HttpResponse()
            if result is False:
                request.session['error'] = str(message)
                SocketUtil.notify(dbdoc_id, session_key=session_key, error=str(message))
            return HttpResponse()

    def get(self, request, **kwargs):
        return HttpResponseRedirect('/')


class SetElementAttributeView(View):
    def post(self, request, **kwargs):
        session_key = request.session.session_key
        form = SetElementAttributeForm(request.POST)
        dbdoc_id = kwargs['document_id']
        controller = SharedVariables.get_dbd_controller(session_key, dbdoc_id)
        if form.is_valid():
            try:
                id = form.cleaned_data['id']
                attribute = form.cleaned_data['attribute']
                value = form.cleaned_data['value']
                result, message = controller.set_element_attr(id, attribute, value)
            except Exception as e:
                request.session['error'] = str(e)
                SocketUtil.notify(dbdoc_id, session_key=session_key, error=str(e))
                return HttpResponse()
            if result is False:
                request.session['error'] = str(message)
                SocketUtil.notify(dbdoc_id, session_key=session_key, error=str(message))
            return HttpResponse()

    def get(self, request, **kwargs):
        return HttpResponseRedirect('/')


class SetElementTextView(View):
    def post(self, request, **kwargs):
        session_key = request.session.session_key
        form = SetElementTextForm(request.POST)
        dbdoc_id = kwargs['document_id']
        controller = SharedVariables.get_dbd_controller(session_key, dbdoc_id)
        if form.is_valid():
            try:
                id = form.cleaned_data['id']
                text = form.cleaned_data['text']
                result, message = controller.set_element_text(id, text)
            except Exception as e:
                request.session['error'] = str(e)
                SocketUtil.notify(dbdoc_id, session_key=session_key, error=str(e))
                return HttpResponse()
            if result is False:
                request.session['error'] = str(message)
                SocketUtil.notify(dbdoc_id, session_key=session_key, error=str(message))
            return HttpResponse()

    def get(self, request, **kwargs):
        return HttpResponseRedirect('/')


class InsertSiblingView(View):
    def post(self, request, **kwargs):
        session_key = request.session.session_key
        form = InsertSiblingForm(request.POST)
        dbdoc_id = kwargs['document_id']
        controller = SharedVariables.get_dbd_controller(session_key, dbdoc_id)
        if form.is_valid():
            try:
                tag = form.cleaned_data['tag']
                id = form.cleaned_data['id']
                after = form.cleaned_data['after']
                result, message = controller.insert_sibling(id, tag, after)
            except Exception as e:
                request.session['error'] = str(e)
                SocketUtil.notify(dbdoc_id, session_key=session_key, error=str(e))
                return HttpResponse()
            if result is None:
                request.session['error'] = str(message)
                SocketUtil.notify(dbdoc_id, session_key=session_key, error=str(message))
            return HttpResponse()

    def get(self, request, **kwargs):
        return HttpResponseRedirect('/')


class InsertTextView(View):
    def post(self, request, **kwargs):
        session_key = request.session.session_key
        form = InsertTextForm(request.POST)
        dbdoc_id = kwargs['document_id']
        controller = SharedVariables.get_dbd_controller(session_key, dbdoc_id)
        if form.is_valid():
            try:
                text = form.cleaned_data['text']
                id = form.cleaned_data['id']
                result, message = controller.insert_text(id, text)
            except Exception as e:
                request.session['error'] = str(e)
                SocketUtil.notify(dbdoc_id, session_key=session_key, error=str(e))
                return HttpResponse()
            if result is False:
                request.session['error'] = str(message)
                SocketUtil.notify(dbdoc_id, session_key=session_key, error=str(message))
            return HttpResponse()

    def get(self, request, **kwargs):
        return HttpResponseRedirect('/')


class SaveView(View):
    def post(self, request, **kwargs):
        session_key = request.session.session_key
        form = SaveForm(request.POST)
        dbdoc_id = kwargs['document_id']
        controller = SharedVariables.get_dbd_controller(session_key, dbdoc_id)
        if form.is_valid():
            try:
                safe = form.cleaned_data['safe']
                result, message = DBDPersistency.save(dbdoc_id, safe)
            except Exception as e:
                request.session['error'] = str(e)
                SocketUtil.notify(dbdoc_id, session_key=session_key, error=str(e))
                return HttpResponse()
            if result is False:
                request.session['error'] = str(message)
                SocketUtil.notify(dbdoc_id, session_key=session_key, error=str(message))
            return HttpResponse()

    def get(self, request, **kwargs):
        return HttpResponseRedirect('/')


class DeleteView(View):
    def post(self, request, **kwargs):
        session_key = request.session.session_key
        dbdoc_id = kwargs['document_id']
        try:
            DBDPersistency.delete(dbdoc_id)
        except Exception as e:
            request.session['error'] = str(e)
            SocketUtil.notify(dbdoc_id, session_key=session_key, error=str(e))

        return HttpResponse()

    def get(self, request, **kwargs):
        return HttpResponseRedirect('/')


class LoadView(View):  # Bozuk
    def post(self, request, **kwargs):
        session_key = request.session.session_key
        dbdoc_id = kwargs['document_id']
        controller = SharedVariables.get_dbd_controller(session_key, dbdoc_id)
        try:
            DBDPersistency.load(dbdoc_id, controller)
        except Exception as e:
            request.session['error'] = str(e)
            SocketUtil.notify(dbdoc_id, session_key=session_key, error=str(e))
        return HttpResponse()

    def get(self, request, **kwargs):
        return HttpResponseRedirect('/')


class UploadView(View):
    def post(self, request):
        session_key = request.session.session_key
        form = UploadForm(request.POST)

        # controller = SharedVariables.get_dbd_controller(session_key, dbdoc_id)
        if form.is_valid():
            try:
                xml = form.cleaned_data['xml_content']
                safe = form.cleaned_data['safe']
                controller = SharedVariables.add_dbd_controller_with_upload(session_key, xml, safe)

                # In case same client is editing the same document in 1+ tabs, after uploading create a new controller.
                # SharedVariables.add_dbd_controller(session_key, controller.get_id())
                # SharedVariables.add_dbd_controller(session_key, dbdoc_id)
            except Exception as e:
                request.session['error'] = str(e)
                print(e)
                return HttpResponseRedirect('/')
            return HttpResponseRedirect('/document/{}'.format(controller.get_id()))

        return HttpResponse("not valid")

    def get(self, request, **kwargs):
        return HttpResponseRedirect('/')


class GetJsonView(View):
    def get(self, request, **kwargs):
        dbdoc_id = kwargs['document_id']
        session_key = request.session.session_key
        controller = SharedVariables.get_dbd_controller(session_key, dbdoc_id)
        doc_name = controller.get_name()

        if not session_key or controller is None:
            return HttpResponseRedirect('/')

        result_json = json.dumps(parse_xml_to_json(controller.dbdoc.content))
        response = {'xml': str(controller.dbdoc), 'doc_name': doc_name,
                    'json_xml': result_json}

        return HttpResponse(json.dumps(response), content_type='application/json')
