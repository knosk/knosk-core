import logging
from abc import ABC, abstractmethod
import json

LOG = logging.getLogger(__name__)

class ChannelMessage(ABC):

    def __init__(self, channel_specific_data=None):
        self.channel_specific_data = channel_specific_data if channel_specific_data is not None else {}

    def to_dict(self):
        """
            Convert to dict
        """
        result = {}
        result.update(self._to_dict())
        result['channel-data'] = self.channel_specific_data
        return result

    @abstractmethod
    def _to_dict(self):
        pass

    @classmethod
    def from_dict(cls, data):
        """
            Convert from dict
        """
        channel_specific_data = data.get('channel-data', {})
        type_handled_specific_data = {key: val if val.strip().lower() != "true" and val.strip().lower() != "false" else bool(val.strip()) for key, val in channel_specific_data.items()}
        entity = cls._from_dict(data)
        if isinstance(entity, tuple):
            return cls(*entity, type_handled_specific_data)
        return cls(entity, type_handled_specific_data)
    
    @classmethod
    def _from_dict(cls, data):
        pass
    
    @staticmethod
    def contains(data):
        pass


class TextMessage(ChannelMessage):
    def __init__(self, text, channel_specific_data=None):
        self.text = text
        super(TextMessage, self).__init__(channel_specific_data)

    def _to_dict(self):
        return {'text': self.text if self.text else ''}

    @classmethod
    def _from_dict(cls, data):
        return data.get('text','')

    @staticmethod
    def contains(data):
        return 'text' in data


class ButtonMessage(ChannelMessage):
    """
        Represent button
    """

    def __init__(self, button, channel_specific_data=None):
        self.button = button
        super(ButtonMessage, self).__init__(channel_specific_data)

    def _to_dict(self):
        return {'button': self.button if self.button else ''}

    @classmethod
    def _from_dict(cls, data):
        return data.get('button','')

    @staticmethod
    def contains(data):
        return 'button' in data


class ButtonsMessage(ChannelMessage):
    child_cls = ButtonMessage
    """
        Represent group of buttons
    """
    def __init__(self, buttons, channel_specific_data=None):
        """
            Buttons are array of arrays
            for example: [["Button1", "Button2"], ["Button3"]]
        """
        self.buttons = buttons
        super(ButtonsMessage, self).__init__(channel_specific_data)

    def convert_from_lists(self, buttons):
        return [self.convert_from_lists(item) if isinstance(item, list) else item.to_dict() for item in buttons]

    @staticmethod
    def convert_to_lists(child_cls, buttons):
        return [ButtonsMessage.convert_to_lists(child_cls, item) if isinstance(item, list) else child_cls.from_dict(item)  for item in buttons]

    def _to_dict(self):
        return {'buttons': self.convert_from_lists(self.buttons)}

    @classmethod
    def _from_dict(cls, data):
        return cls.convert_to_lists(cls.child_cls, data.get('buttons', []))

    @staticmethod
    def contains(data):
        return 'buttons' in data


class KeyboardMessage(ChannelMessage):
    """
        Represent one button in keyboard
    """
    def __init__(self, keyboard, channel_specific_data=None):
        self.keyboard = keyboard
        super(KeyboardMessage, self).__init__(channel_specific_data)

    def _to_dict(self):
        return {'keyboard': self.keyboard if self.keyboard else ''}

    @classmethod
    def _from_dict(cls, data):
        return data.get('keyboard','')

    @staticmethod
    def contains(data):
        return 'keyboard' in data


class KeyboardsMessage(ChannelMessage):
    child_cls = KeyboardMessage
    """
        Represent group of keyboard buttons
    """
    def __init__(self, keyboards, channel_specific_data=None):
        self.keyboards = keyboards
        super(KeyboardsMessage, self).__init__(channel_specific_data)

    def convert_from_lists(self, keyboards):
        return [self.convert_from_lists(item) if isinstance(item, list) else item.to_dict() for item in keyboards]

    @staticmethod
    def convert_to_lists(child_cls, keyboards):
        return [KeyboardsMessage.convert_to_lists(child_cls, item) if isinstance(item, list) else child_cls.from_dict(item)  for item in keyboards]

    def _to_dict(self):
        return {'keyboards': self.convert_from_lists(self.keyboards)}

    @classmethod
    def _from_dict(cls, data):
        return cls.convert_to_lists(cls.child_cls, data.get('keyboards', []))

    @staticmethod
    def contains(data):
        return 'keyboards' in data


class AudioMessage(ChannelMessage):
    def __init__(self, url, channel_specific_data=None):
        self.url = url
        super(AudioMessage, self).__init__(channel_specific_data)

    def _to_dict(self):
        return {'audio': self.url if self.url else ''}

    @classmethod
    def _from_dict(cls, data):
        return data.get('audio','')

    @staticmethod
    def contains(data):
        return 'audio' in data


class VideoMessage(ChannelMessage):
    def __init__(self, url, channel_specific_data=None):
        self.url = url
        super(VideoMessage, self).__init__(channel_specific_data)

    def _to_dict(self):
        return {'video': self.url if self.url else ''}

    @classmethod
    def _from_dict(cls, data):
        return data.get('video','')

    @staticmethod
    def contains(data):
        return 'video' in data
        

class ImageMessage(ChannelMessage):
    def __init__(self, url, channel_specific_data=None):
        self.url = url
        super(ImageMessage, self).__init__(channel_specific_data)

    def _to_dict(self):
        return {'image': self.url if self.url else ''}

    @classmethod
    def _from_dict(cls, data):
        return data.get('image','')

    @staticmethod
    def contains(data):
        return 'image' in data


class LocationMessage(ChannelMessage):
    def __init__(self, lt, lg, channel_specific_data=None):
        self.lt = lt
        self.lg = lg
        super(LocationMessage, self).__init__(channel_specific_data)

    def _to_dict(self):
        return {'location': {'lt': self.lt, 'lg': self.lg}}

    @classmethod
    def _from_dict(cls, data):
        return (data['location']['lt'], data['location']['lg'])

    @staticmethod
    def contains(data):
        return 'location' in data


class MessageBox(ChannelMessage):
    child_cls = [TextMessage, ButtonMessage, ButtonsMessage,\
        KeyboardMessage, KeyboardsMessage, AudioMessage, VideoMessage, ImageMessage,\
        LocationMessage]
    text_cls = TextMessage

    """
        It's group of messages
    """
    def __init__(self, messages=None, channel_specific_data=None):
        self.messages = messages if messages is not None else []
        super(MessageBox, self).__init__(channel_specific_data)

    def _to_dict(self):
        return {"messages":[msg.to_dict() for msg in self.messages]}

    @classmethod
    def _from_dict(cls, data):
        messages = []
        for msg in data['messages']:
            found_types = [mt for mt in cls.child_cls if mt.contains(msg)]
            if found_types:
                msg_type = found_types[0]
                messages.append(msg_type.from_dict(msg))
        return messages
    
    @staticmethod
    def contains(data):
        return 'messages' in data

    @classmethod
    def from_text_to_message(cls, text):
        try:
            data = json.loads(text)
            LOG.debug("Parse message data %s" % data)
            return cls.from_dict(data)
        except json.decoder.JSONDecodeError as jer:
            LOG.debug("Can't parse json it seems it's just text %s" % jer)

        return cls.from_text(text)

    @classmethod
    def from_text(cls, text):
        tm = cls.text_cls(text)
        return cls(messages=[tm])

    def to_json(self):
        return json.dumps(self.to_dict())
