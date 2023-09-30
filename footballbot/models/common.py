from copy import deepcopy

class SerializerAlchemyMixin:
    drop_list = ['_sa_instance_state']

    def serialize(self):
        dict_copy = deepcopy(self.__dict__)
        for key in self.drop_list:
            dict_copy.pop(key, None)
        return dict_copy