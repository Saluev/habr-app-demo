class ClientConverter(object):

    def to_json(self, obj):
        return {
            k: v
            for k, v in obj.__dict__.items()
            if v is not None
        }
