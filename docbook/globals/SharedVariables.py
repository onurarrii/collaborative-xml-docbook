''' Behaves as a singleton service.
Use this class for globally defined variables.
But its main usage will be holding global dbdoc objects. '''
import requests

from docbook.util import SocketUtil


class SharedVariables:
    ''' dbdoc_list stores JSON objects in form of:
    [{
        "id":{
            "changed": False,
            "content": XmlTree
            }
    }, ...]
    '''
    dbdoc_list = {}

    ''' dbdcontroller_notifier_list stores JSON objects in form of: 
    [{
        "id":notifier_functions[]    
    }, ...]
    '''
    dbdcontroller_notifier_list = {}

    ''' controller_list stores JSON objects in form of:
        "session_id" : DBDController object
    '''
    controller_list = {}

    @staticmethod
    def add_dbdoc(dbdoc, changed):
        dbdoc_id = dbdoc.get_id()
        SharedVariables.dbdoc_list[dbdoc_id] = {'changed': changed, 'content': dbdoc}

    @staticmethod
    def delete_dbdoc(dbdoc_id):
        try:
            SharedVariables.dbdoc_list.pop(dbdoc_id)
        finally:
            pass

    @staticmethod
    def get_dbdoc(dbdoc_id):
        try:
            return SharedVariables.dbdoc_list[dbdoc_id]['content']
        except KeyError:
            return None

    @staticmethod
    def get_all_dbdoc(only_dbdocs=False):
        if only_dbdocs is True:
            return [SharedVariables.dbdoc_list[i]['content'] for i in SharedVariables.dbdoc_list]
        return SharedVariables.dbdoc_list

    @staticmethod
    def add_dbdcontroller_notifier(dbdoc_id, notifier, callback):
        try:
            notifier_list = SharedVariables.dbdcontroller_notifier_list[dbdoc_id]
            if notifier_list is None:
                notifier_list = []
            notifier_list.append((notifier, callback))
            SharedVariables.dbdcontroller_notifier_list[dbdoc_id] = notifier_list
        except KeyError:
            SharedVariables.dbdcontroller_notifier_list[dbdoc_id] = [(notifier, callback)]

    ''' This method should only be called by DBDController objects but nothing more.'''

    @staticmethod
    def notify_controllers_on_change(dbdoc_id, dbdoc, loaded=False, owner_notification=None):
        SocketUtil.notify_all(dbdoc_id)
        if SharedVariables.dbdoc_list[dbdoc_id] is not None:
            SharedVariables.dbdoc_list[dbdoc_id]['changed'] = loaded is False
            SharedVariables.dbdoc_list[dbdoc_id]['content'] = dbdoc
            for key in SharedVariables.dbdcontroller_notifier_list:
                if key != dbdoc_id:
                    continue
                notifier_list = SharedVariables.dbdcontroller_notifier_list[key]
                for notifier, callback in notifier_list:
                    with notifier:
                        callback()
                        if owner_notification is not None and owner_notification == notifier:
                            continue
                        notifier.notify()

                        # notify all the DBDControllers which are attached to the xml with this id.

    @staticmethod
    def add_dbd_controller_with_upload(session_key, xml_content, safe = False):
        from docbook.dbd.DBDController import DBDController


        controller = DBDController(xml_content=xml_content, safe=safe)
        try:
            SharedVariables.controller_list[session_key].append(controller)
        except KeyError:
            SharedVariables.controller_list[session_key] = [controller]
        return controller

    @staticmethod
    def add_dbd_controller(session_key, dbdoc_id):
        from docbook.dbd.DBDController import DBDController

        try:
            controller_list = SharedVariables.controller_list[session_key]
            for c in controller_list:
                if dbdoc_id == c.get_id():
                    return c
        except KeyError:
            pass
        controller = DBDController(dbdoc_id)
        try:
            SharedVariables.controller_list[session_key].append(controller)
        except KeyError:
            SharedVariables.controller_list[session_key] = [controller]
        return controller

    @staticmethod
    def get_dbd_controller(session_key, dbdoc_id):
        try:
            c_list = SharedVariables.controller_list[session_key]
            for c in c_list:
                if dbdoc_id == c.get_id():
                    return c
            return None
        except KeyError:
            return None

    ''' :returns controllers attached to a user '''

    @staticmethod
    def get_controllers_by_session_id(session_id):
        return SharedVariables.controller_list[session_id]

    @staticmethod
    def get_controllers_by_document_id(document_id):
        lst = []
        for key in SharedVariables.controller_list:
            for controller in SharedVariables.controller_list[key]:
                try:
                    if controller.get_id() == document_id:
                        lst.append(controller)
                except KeyError:
                    continue
        return lst

    ''' call this method when db_doc is saved to db '''

    @staticmethod
    def on_db_save(dbdoc_id):
        try:
            SharedVariables.dbdoc_list[dbdoc_id]['changed'] = False
        except:
            pass

    @staticmethod
    def to_string():
        return str(SharedVariables.dbdoc_list) + '\n' + str(SharedVariables.dbdcontroller_notifier_list)
