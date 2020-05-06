''' Use this util for validating xml contents. '''
from lxml import etree


class ValidationUtil:
    attributes = {
        'page': ['id', 'type', 'xmlns'],
        'section': ['id'],
        'info': ['id'],
        'credit': ['id', 'type'],
        'title': ['id', 'type'],
        'license': ['id'],
        'desc': ['id'],
        'code': ['id'],
        'media': ['type', 'mime', 'src', 'height', 'width'],
        'list': ['type'],
        'cite': ['date', 'ref'],
        'link': ['xref', 'hre']
    }

    tags = ['page', 'section', 'info', 'credit', 'title', 'license', 'desc', 'revision', 'years', 'email', 'name',
            'code', 'example', 'media', 'p', 'quote', 'comment', 'note', 'synopsis', 'list', 'steps', 'terms', 'item',
            'cite', 'em', 'link', 'gui']

    optional = {  # stands for question mark in the text
        'page': ['info'],
        'section': ['info'],
        'info': ['desc'],
        'credit': ['years'],
        'quote': ['title', 'cite'],
        'comment': ['title', 'cite']
    }

    asterix = {  #
        'page': ['section'],
        'section': ['section'],
        'info': ['credit'],
        'credit': ['email'],
        'list': ['item'],
        'steps': ['item'],
        'terms': ['item']
    }

    # these elements MUST contain block text. stands for '+'
    must_contain_block = ['example', 'quote', 'comment', 'note', 'synopsis', 'item']

    block = ['code', 'comment', 'example', 'figure', 'list', 'media', 'note', 'p', 'quote', 'steps', 'terms',
             'synopsis', 'gui']

    # these elements can only contain inline text (plain text)
    inline_text = ['title', 'license', 'revision', 'years', 'email', 'name', 'code', 'p', 'cite', 'em', 'link', 'gui']

    # these elements must contain given tags
    must_contain_tag = {
        'page': ['title'],
        'section': ['title', 'block_text'],
        'info': ['license', 'revision'],
        'credit': ['name'],
        'media': ['block_text'],
        'desc': ['block_text']
    }

    # elements are only allowed to have given tags
    allowed_tags = {
        'page': ['info', 'title', 'section'],
        'section': ['info', 'title', 'section', block],
        'info': ['desc', 'credit', 'license', 'revision'],
        'credit': ['name', 'email', 'years'],
        'desc': block,
        'example': block,
        'media': block,
        'list': ['item'],
        'steps': ['item'],
        'terms': ['item'],
        'item': block,
    }

    @staticmethod
    def validate_attribute(tag, attr):
        if attr == 'id':  # for our implementation, each element can contain id
            return True
        try:
            return attr in ValidationUtil.attributes[tag]
        except KeyError:
            return False
        except Exception as e:
            print(e)
            return False

    @staticmethod
    def validate_tag(tag):
        return tag in ValidationUtil.tags

    # param element is in type lxml tree element
    @staticmethod
    def validate_block_text(element):
        tag_name = str(etree.QName(element.tag).localname)
        if tag_name not in ValidationUtil.must_contain_block:  # do not need to check
            return True, ["Tag {} is valid.".format(tag_name)]
        for child in element:
            child_tag_name = str(etree.QName(child.tag).localname)
            if child_tag_name in ValidationUtil.block:
                return True, ["Tag {} is valid.".format(tag_name)]
        return False, ["'{}' tag should be instantiated with at least one block text element.".format(tag_name)]

    # iterate over element and call this for each child.
    @staticmethod
    def validate_asterix(element):
        tag_name = str(etree.QName(element.tag).localname)
        child_tags = []
        for child in element:  # fill child_tags list
            child_name = str(etree.QName(child.tag).localname)
            child_tags.append(child_name)
        for tag in child_tags:
            try:  # if tag is optional for this element and there are multiple return False
                if tag in ValidationUtil.optional[tag_name] and child_tags.count(tag) > 1:
                    return False
            except KeyError:
                continue

        return True

    @staticmethod
    def validate_inline_text(element):
        '''
        Some elements contain only inline text and no children
        This function checks this condition for given element
        '''
        tag_name = str(etree.QName(element.tag).localname)
        wrong_texts = ['\n', '', None]
        if tag_name not in ValidationUtil.inline_text:  # do not need to check
            return True, 'Tag is valid'
        child_nodes = len(list(element))
        if child_nodes > 0:
            return False, "Tag {} can not have child nodes.".format(tag_name)
        if element.text in wrong_texts:
            return False, "Tag {} can not be empty.".format(tag_name)
        return True, "Tag is valid"

    @staticmethod
    def validate_optional(element):
        """
        Validates if given element has its optional (0 or one) children
        """
        error_list = list()
        tag_name = str(etree.QName(element.tag).localname)

        if tag_name not in ValidationUtil.optional.keys():  # do not need to check
            return True, ['Tag is valid']

        element_tag_list = [etree.QName(child.tag).localname for child in list(element)]
        optional_tags = ValidationUtil.optional[tag_name]
        for ot in optional_tags:
            tag_count = element_tag_list.count(ot)
            if tag_count > 1:
                error_list.append("There can't be more than one instance of tag '{}' inside '{}'".format(ot, tag_name))

        if len(error_list) == 0:
            return True, ['Tag is valid']
        else:
            return False, error_list

    @staticmethod
    def block_element_count(tag_list):
        """
        Helper function that counts block elements inside a list
        """
        count = 0
        for t in tag_list:
            if t in ValidationUtil.block:
                count += 1
        return count

    @staticmethod
    def validate_must_contain(element):
        """
        Some elements have tags that they must contain,
        This function checks if they have all those tags as their children
        """

        error_list = list()
        tag_name = str(etree.QName(element.tag).localname)

        if tag_name not in ValidationUtil.must_contain_tag.keys():  # do not need to check
            return True, ["Tag '{}' is valid.".format(tag_name)]

        element_tag_list = [etree.QName(child.tag).localname for child in list(element)]
        must_contain_tags = ValidationUtil.must_contain_tag[tag_name]

        for tag in must_contain_tags:
            if tag == 'block_text':
                tag_count = ValidationUtil.block_element_count(element_tag_list)
            else:
                tag_count = element_tag_list.count(tag)

            if tag_count > 1:
                error_list.append("Tag '{}' can not appear more than once inside tag '{}'".format(tag, tag_name))
            elif tag_count < 1:
                error_list.append("Tag '{}' must be a child of tag '{}'".format(tag, tag_name))

        if len(error_list) == 0:
            return True, ["Tag '{}' is valid.".format(tag_name)]
        else:
            return False, error_list

    @staticmethod
    def validate_allowed_tags(element):
        """
        All elements have a list of tags that they can have as children
        This function checks if given element has correct tags as its children
        """
        error_list = list()
        tag_name = str(etree.QName(element.tag).localname)

        if tag_name not in ValidationUtil.allowed_tags.keys():  # do not need to check
            return True, ["Tag '{}' is valid.".format(tag_name)]

        element_tag_list = [etree.QName(child.tag).localname for child in list(element)]
        allowed = ValidationUtil.allowed_tags[tag_name]
        for tag in element_tag_list:
            if tag not in allowed:
                error_list.append("Tag '{}' can not be a child of Tag '{}'.".format(tag, tag_name))

        if len(error_list) == 0:
            return True, ["Tag '{}' is valid.".format(tag_name)]
        else:
            return False, error_list

    @staticmethod
    def validate(dbdoc):
        '''
        checks all validation rules and returns a tuple such that (False, list of errors) if there is any errors
        '''
        error_list = list()
        is_valid = True
        tag = etree.QName(dbdoc).localname
        if tag != "page":
            is_valid = False
            error_list.append("Document should start with 'page' tag.")
        for child in dbdoc.iter():
            tag = etree.QName(child.tag).localname
            if not ValidationUtil.validate_tag(tag):
                is_valid = False
                error_list.append("Tag '{}' is not valid.".format(tag))

            for attr in child.attrib:
                if not ValidationUtil.validate_attribute(tag, attr):
                    is_valid = False
                    error_list.append("Attribute '{}' of tag '{}' is not valid.".format(attr, tag))

            inline_text_result, message = ValidationUtil.validate_inline_text(child)
            if not inline_text_result:
                is_valid = False
                error_list.append(message)

            block_text_result, message_list = ValidationUtil.validate_block_text(child)

            if not block_text_result:
                is_valid = False
                error_list.extend(message_list)

            optional_result, message_list = ValidationUtil.validate_optional(child)

            if not optional_result:
                is_valid = False
                error_list.extend(message_list)

            must_contain_result, message_list = ValidationUtil.validate_must_contain(child)

            if not must_contain_result:
                is_valid = False
                error_list.extend(message_list)

            allowed_tags_result, message_list = ValidationUtil.validate_allowed_tags(child)

            if not allowed_tags_result:
                is_valid = False
                error_list.extend(message_list)

        if is_valid:
            return True, "The given text is valid."
        else:
            return False, error_list
