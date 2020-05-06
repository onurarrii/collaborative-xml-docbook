from threading import Condition
import lxml.etree as ET

from docbook.dbd.DBDPersistency import DBDPersistency
from docbook.dbd.DBDoc import DBDoc
from docbook.globals.SharedVariables import SharedVariables
from docbook.util.ValidationUtil import ValidationUtil


class DBDController:
    """
    DBD Controller
    """
    count = 0  # for test purposes only delete it.

    def __init__(self, attached_id="NEW", xml_content = None, safe = False):
        if xml_content is not None:
            messages = []
            try:
                if not safe:
                    is_valid, messages = ValidationUtil.validate(ET.fromstring(xml_content))
                else:
                    is_valid = True
            except:
                raise Exception(["The given string could not be converted into an xml."])
            if is_valid:
                self.count = DBDController.count
                DBDController.count += 1
                self.notification = Condition()
                dbdoc = DBDoc(xml_content)
                SharedVariables.add_dbdoc(dbdoc, True)
                self.attached_id = dbdoc.get_id()
                self.dbdoc = dbdoc
                SharedVariables.add_dbdcontroller_notifier(self.attached_id, self.notification, self.on_dbdoc_change)
            else:
                raise Exception(messages)
        else:
            self.count = DBDController.count
            DBDController.count += 1
            self.notification = Condition()
            if attached_id == "NEW":
                dbdoc = DBDoc()
                SharedVariables.add_dbdoc(dbdoc, True)
                self.attached_id = dbdoc.get_id()
                self.dbdoc = dbdoc
                SharedVariables.add_dbdcontroller_notifier(self.attached_id, self.notification, self.on_dbdoc_change)
            else:
                if SharedVariables.get_dbdoc(attached_id) is None:
                    try:
                        DBDPersistency.load(attached_id)
                        self.attached_id = attached_id
                        self.dbdoc = SharedVariables.get_dbdoc(attached_id)
                        SharedVariables.add_dbdcontroller_notifier(self.attached_id, self.notification, self.on_dbdoc_change)
                    except:
                        raise Exception('Cannot be attached to a non existing dbdoc')
                else:
                    self.attached_id = attached_id
                    self.dbdoc = SharedVariables.get_dbdoc(attached_id)
                    SharedVariables.add_dbdcontroller_notifier(self.attached_id, self.notification, self.on_dbdoc_change)



    ''' xmlcontent is in type string '''

    def upload(self, xmlcontent, safe=False):
        messages = []
        try:
            if not safe:
                is_valid,messages = ValidationUtil.validate(ET.fromstring(xmlcontent))
            else:
                is_valid = True
        except:
            return False, ["The given string could not be converted into an xml."]
        if is_valid:
            dbdoc = DBDoc(xmlcontent)
            SharedVariables.add_dbdoc(dbdoc, True)
            self.attached_id = dbdoc.get_id()
            self.dbdoc = dbdoc
            return True, "Document Uploaded."
        return False, messages

    def on_dbdoc_change(self):
        """ Use this for notifying DBDController when the xml it is attached to is changed """
        '''
            Since dbdoc's are references(pass by reference), even without this notification 
            self.dbdoc will be updated automatically.
            But for further usages, this implementation may help.
        '''
        self.dbdoc = SharedVariables.get_dbdoc(self.attached_id)

    def on_upload_dbdoc_request(self, function):
        result = function()
        if result[0]:
            SharedVariables.notify_controllers_on_change(self.attached_id, self.dbdoc, False, self.notification)
        return result

    ''' The rest behaves as an interface for DBDoc. use on_upload_dbdoc_request with appropriate inputs when dbdoc is tried to be uploaded. '''

    def get_id(self):
        return self.attached_id

    def get_name(self):
        return self.dbdoc.get_name()

    def set_name(self, name):
        def func():
            return self.dbdoc.set_name(name)

        return self.on_upload_dbdoc_request(func)

    def get_element_by_id(self, id='/'):
        return self.dbdoc.get_element_by_id(id)

    def get_element_by_xpath(self, xpath):
        return self.dbdoc.get_element_by_xpath(xpath)

    def delete_element_by_id(self, id):
        def func():
            return self.dbdoc.delete_element_by_id(id)

        return self.on_upload_dbdoc_request(func)

    def delete_element_attr(self, id, attr):
        def func():
            return self.dbdoc.delete_element_attr(id, attr)

        return self.on_upload_dbdoc_request(func)

    def set_element_attr(self, id, attr, value):
        def func():
            return self.dbdoc.set_element_attr(id, attr, value)

        return self.on_upload_dbdoc_request(func)

    def set_element_text(self, id, text):
        def func():
            return self.dbdoc.set_element_text(id, text)

        return self.on_upload_dbdoc_request(func)

    def insert_child(self, id, tag, append=True):
        def func():
            return self.dbdoc.insert_child(id, tag, append)

        return self.on_upload_dbdoc_request(func)

    def insert_sibling(self, id, tag, after=True):
        def func():
            return self.dbdoc.insert_sibling(id, tag, after)

        return self.on_upload_dbdoc_request(func)

    def insert_text(self, id, text):
        def func():
            return self.dbdoc.insert_text(id, text)

        return self.on_upload_dbdoc_request(func)

    def __str__(self):
        return str("Name: {}\nContent: {}\n".format(self.dbdoc.name, self.dbdoc))
