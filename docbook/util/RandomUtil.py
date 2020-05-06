from uuid import uuid4


class RandomUtil:
    ''' A Util that generates random ids'''
    @staticmethod
    def generate_id():
        return uuid4()