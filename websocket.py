#!/usr/bin/env python3
#
"""Derived from tornado websocket chat demo
"""

import logging
import tornado.escape
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.websocket
import os.path
import uuid

from tornado.options import define, options

define("port", default=9000, help="run on the given port", type=int)


class Application(tornado.web.Application):
    def __init__(self):
        # set handlers based on the URI path
        handlers = [(r"/", MainHandler), (r"/documents", DocumentSocketHandler)]
        settings = dict(
            cookie_secret="db0b04103c079c743f2d6562bb5315c",
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies=False,
        )
        super(Application, self).__init__(handlers, **settings)


class MainHandler(tornado.web.RequestHandler):
    '''handler for regular http requests (for getting index.html)'''

    def get(self):
        # no authentication in system. Just assign a random username per browser connection
        user = str(uuid.uuid4())[:8]
        # self.render("index.html", username=user, entries=ChatSocketHandler.entries)

    def check_origin(self, origin):
        return True

    def post(self, *args, **kwargs):

        data = tornado.escape.json_decode(self.request.body)
        print(data)
        try:
            data_id = data['id']
        except KeyError:
            data_id = None
        try:
            session_key = data['session_key']
            error = data['error']
        except KeyError:
            session_key = None
            error = None
        try:
            DocumentSocketHandler.notify(data_id, session_key, error)
        except:
            print('Hata aldik')


class DocumentSocketHandler(tornado.websocket.WebSocketHandler):

    ''' holds document_id -> controller(socket)[] .
        when a document is changed notify all the controllers
        (basically traverse controllers[id] list)'''
    controllers = {}

    def check_origin(self, origin):
        return True

    def get_compression_options(self):
        # Non-None enables compression with default options.
        return {}

    def open(self):
        pass

    def on_close(self):
        logging.info('Close request')
        for key in DocumentSocketHandler.controllers.keys():
            try:
                for pair in DocumentSocketHandler.controllers[key]:
                    controller = pair[0]
                    if controller == self:
                        DocumentSocketHandler.controllers[key].remove(pair)
            except:
                continue

    '''
    @:param message is a json object containing two fields: 
    {
     "id": "e2183100sf848fd93",
     "operation": "add" or "update"
    }
    '''

    def on_message(self, message):
        '''when a new message (operation) is received from browser'''
        print(message)
        logging.info("got message %r", message)
        parsed_message = tornado.escape.json_decode(message)
        op = ""
        dbdoc_id = ""
        try:
            op = parsed_message["operation"]
            dbdoc_id = parsed_message["id"]
            session_key = parsed_message["session_key"]
        except:  # If an exception is raised, then JSON object is wrong
            return

        if op == 'add':
            try:
                for pair in DocumentSocketHandler.controllers[dbdoc_id]:
                    if pair[1] == session_key:
                        self.write_message({'redirect': True})
                        return

                DocumentSocketHandler.controllers[dbdoc_id].append((self, session_key))
            except KeyError:
                DocumentSocketHandler.controllers[dbdoc_id] = [(self, session_key)]
        elif op == 'update':
            try:
                DocumentSocketHandler.notify(dbdoc_id)
            except:
                self.write_message({'message': 'An error occured while notifications others'})

    # if session_key is None, then notify all the controllers
    @staticmethod
    def notify(dbdoc_id, session_key=None, error=None):
        try:
            for controller_pair in DocumentSocketHandler.controllers[dbdoc_id]:
                controller = controller_pair[0]
                if session_key is None:
                    controller.write_message({'message': 'Your document has been changed.'})
                elif session_key == controller_pair[1]:
                    # if only one socket is notified, than this means that the controller tried to do an invalid operation
                    controller.write_message({'error': error})
                    break
        except:
            print('Unexpected error')


def main():
    tornado.options.parse_command_line()
    app = Application()
    app.listen(options.port)
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
