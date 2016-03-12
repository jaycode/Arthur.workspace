"""
This module contains ClientInstruction class.
"""
import json

class ClientInstruction():
    """An object that can be returned to front end to give instructions.

    ClientInstruction object can tell client what to do when command has been processed in back-end.
    There are of course really long operations where it is better to update things asynchronously,
    like running the learning process etc.
    """
    _value = {
        'message': "Message to show in console area"
    }
    def __init__(self, value):
        """Initializes object.
        """
        self.set_value(value)

    def set_value(self, allvalues_or_key, value='[emptyvalue]'):
        """Sets _value attribute.
        """
        if value == '[emptyvalue]':
            self._value = allvalues_or_key
        else:
            self._value[allvalues_or_key] = value
        return self._value

    def get_value(self, key = None):
        """Gets _value attribute.
        """
        if key is not None:
            if key in self._value:
                return self._value[key]
            else:
                return None
        else:
           return self._value

    def get_message(self):
        """Gets message from _value attribute.
        """
        return self._value['message']

    def set_message(self, new_message):
        """Sets message in _value attribute.
        """
        self._value['message'] = new_message
        return self._value['message']

    def to_json(self):
        """Gets _value attribute in json form.
        """

        return json.dumps(self._value)
