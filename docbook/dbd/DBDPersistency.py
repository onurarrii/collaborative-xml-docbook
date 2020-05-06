from docbook.config import DBConnector
from docbook.dbd.DBDoc import DBDoc
from docbook.globals.SharedVariables import SharedVariables
from docbook.util.ValidationUtil import ValidationUtil


class DBDPersistency:
    """
    Class Explanation
    """

    def __init__(self):
        pass

    @staticmethod
    def save(id, safe=False):
        """
        :param safe: is for saving document without validation, put in here for testing purposes. If
                     safe == True the function does not validate the xml file
        """
        dbdoc = SharedVariables.get_dbdoc(id)
        if dbdoc is None:
            return False, ['You cannot try to delete a non-existing document.']

        with dbdoc.mutex:
            name = dbdoc.get_name()
            is_valid, message_list = ValidationUtil.validate(dbdoc.content)
            if not is_valid and not safe:
                return False, message_list
            dbdoc = str(dbdoc)
            connection = DBConnector.get_connection()
            cursor = connection.cursor()
            try:
                statement = "INSERT INTO xml_doc VALUES(%s,%s,%s)"
                cursor.execute(statement, (id, name, dbdoc))
            except Exception as e:
                connection.rollback()  # duplicated key error, update is required
                try:
                    statement = "UPDATE xml_doc SET name = %s, content = %s WHERE id = %s"
                    cursor.execute(statement, (name, dbdoc, id))
                except:
                    return False, ["An error occured when saving document"]
            connection.commit()
            SharedVariables.on_db_save(id)
            return True, ["Everything is okay"]

    @staticmethod
    def load(id, owner=None):  # owner should be in type DBDController
        connection = DBConnector.get_connection()
        cursor = connection.cursor()
        statement = "Select * from xml_doc where id = %s"
        try:
            cursor.execute(statement, (id,))
            id, name, content = cursor.fetchone()
            dbdoc = DBDoc(content)
            dbdoc.set_name(name)
            dbdoc.id = id
            notification = owner.notification if owner is not None else None
            SharedVariables.add_dbdoc(dbdoc, False)
            SharedVariables.notify_controllers_on_change(dbdoc.get_id(), dbdoc, True, notification)
        except Exception as e:
            raise Exception('Cannot load a non-saved document.')

    @staticmethod
    def list():
        connection = DBConnector.get_connection()
        cursor = connection.cursor()
        statement = "Select * from xml_doc"
        try:
            cursor.execute(statement)
            lst = []
            for i in cursor.fetchall():
                dbdoc = DBDoc(i[2])
                dbdoc.set_name(i[1])
                dbdoc.id = i[0]
                lst.append(dbdoc)
            return lst
        except Exception as e:
            print(e)

    @staticmethod
    def listmem(dirty=False):
        dbdoc_dict = SharedVariables.get_all_dbdoc()
        result = []
        if dirty:
            for id in dbdoc_dict:
                docJSON = dbdoc_dict[id]
                if docJSON['changed'] is False:
                    continue
                result.append((id, docJSON['content']))
            pass
        else:
            for id in dbdoc_dict:
                docJSON = dbdoc_dict[id]
                result.append((id, docJSON['content']))
        return result

    @staticmethod
    def delete(id):
        connection = DBConnector.get_connection()
        cursor = connection.cursor()
        statement = "DELETE FROM xml_doc where id=%s"
        try:
            cursor.execute(statement, (id,))
            connection.commit()
        except Exception as e:
            print(e)
