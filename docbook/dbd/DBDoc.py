from threading import RLock

import lxml.etree as ET

from docbook.util.RandomUtil import RandomUtil


class DBDoc:
    """
    Class Explanation
    """

    def __init__(self, xmlcontent=None):
        self.id = str(RandomUtil.generate_id())
        self.mutex = RLock()
        if xmlcontent is None:
            xml_string = '<page xmlns="http://projectmallard.org/1.0/"></page>'
        else:
            xml_string = xmlcontent
        self.content = ET.fromstring(xml_string)
        if self.get_element_by_id('/').get('id'):
            self.id = self.get_element_by_id('/').get('id')
        self.set_content_ids_on_upload()  # add id to tags that does not have id as their attribute
        root = self.get_element_by_id('/')
        root.set('id', self.id)
        self.name = 'Unnamed'  # TODO: None?

    def get_id(self):
        with self.mutex:
            return self.id

    def get_name(self):
        with self.mutex:
            return self.name

    def set_name(self, name):
        with self.mutex:
            if type(name) is str:
                self.name = name
                return True, 'Name is changed.'
            return False, 'Name parameter should be string'

    def get_element_by_id(self, id='/'):
        with self.mutex:
            if id == '/':
                return self.content

            for elem in self.content.iter():
                try:
                    elem_id = elem.attrib['id']
                    if elem_id == id:
                        return elem
                except KeyError:
                    pass
            return None

    def get_element_by_xpath(self, xpath):
        with self.mutex:
            try:
                return self.content.find(xpath)
            except:
                return None
    def delete_element_by_id(self, id):
        with self.mutex:
            if id == self.id:
                return False, 'Deletion of page element is forbidden.'
            elem = self.get_element_by_id(id)
            if elem is not None:
                elem.getparent().remove(elem)
                return True, 'Element removed.'
            else:
                return False, 'Nothing was found with given id.'

    def delete_element_attr(self, id, attr):
        with self.mutex:
            if attr == 'id':
                return False, 'Id attribute cannot be deleted.'

            elem = self.get_element_by_id(id)

            if elem is not None:
                try:
                    elem.attrib.pop(attr)
                    return True, 'Attribute deleted.'
                except KeyError:
                    return False, 'Attribute not found'
            else:
                return False, 'Nothing was found with given id.'

    def set_element_attr(self, id, attr, value):
        with self.mutex:
            if attr == 'id' and id == self.id:
                return False, 'Document id cannot be changed after it is initiliazed.'
            """
            prevent content from containing duplicated ids
            """
            if attr == 'id' and self.get_element_by_id(value) is not None:
                return False, 'Duplicated id is not allowed.'

            elem = self.get_element_by_id(id)
            if elem is not None:
                try:
                    elem.set(attr, value)
                except:
                    return False, "Attribute name is invalid"
                return True, 'Attribute added.'
            else:
                return False, 'Nothing was found with given id.'

    def set_element_text(self, id, text):

        """
        Gets an id and a text, sets the given text as the text of element with given id.
        :return: a tuple that gives information about whether the operation was successful or not
        """
        with self.mutex:
            elem = self.get_element_by_id(id)
            if elem.getchildren():
                return False, 'Inner texts of elements with children can not be set.'
            if elem is not None:
                elem.text = text
                return True, 'Text added.'
            else:
                return False, 'Nothing found with given id.'

    def insert_child(self, id, tag, append=True):
        """
        If append = True adds to the end of tag, else add to 0th index
        """
        # checks if a tag is given
        with self.mutex:
            if tag is None:
                return None, "Tag is not given"

            try:
                new_element = ET.Element(tag)
            except:
                return None, "Tag is invalid"
            element_id = self.generate_elem_id()
            new_element.set("id", element_id)

            elem = self.get_element_by_id(id)

            if elem is not None:
                if elem.getchildren():
                    if append:
                        elem.getchildren()[-1].addnext(new_element)
                    else:
                        elem.getchildren()[0].addprevious(new_element)
                else:
                    if append:
                        elem.append(new_element)
                    else:
                        elem.insert(0, new_element)
                return element_id, "Element with tag {} is inserted.".format(tag)

            else:
                return None, "Sibling element could not be found."

    def insert_sibling(self, id, tag, after=True):
        with self.mutex:
            if tag is None:
                return None, "Tag is not given"
            try:
                new_element = ET.Element(tag)
            except:
                return None, "Tag is invalid"
            element_id = self.generate_elem_id()
            new_element.set("id", element_id)

            elem = self.get_element_by_id(id)

            if elem is not None:
                if after:
                    elem.addnext(new_element)
                else:
                    elem.addprevious(new_element)
                return element_id, "Element is inserted successfully."

            else:
                return None, 'Nothing found with given id.'

    def insert_text(self, id, text):
        with self.mutex:
            elem = self.get_element_by_id(id)
            if elem is not None:
                elem.tail = text
                return True, "Text is added to tail"
            else:
                return False, 'Nothing found with given id.'

    '''
     Traverses the whole xml and generates a fresh new id for the new element.
    '''

    def generate_elem_id(self):
        '''traverse and find maximum integer'''
        with self.mutex:
            max_id = -1
            for elem in self.content.iter():
                try:
                    id = int(elem.attrib['id'])
                    if id >= max_id:
                        max_id = id
                except:
                    pass
            return str(max_id + 1)

    ''' called when there occurs a change in dbdoc '''

    def set_content_ids_on_upload(self):
        with self.mutex:
            for element in self.content.iter():
                id = element.get('id')
                if id is None:
                    new_id = self.generate_elem_id()
                    element.set('id', new_id)

    def __str__(self):
        with self.mutex:
            return ET.tostring(self.content, pretty_print=True).decode('utf-8')
