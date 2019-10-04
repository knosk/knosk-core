import logging
import time
from knosk.core import DialogForm

LOG = logging.getLogger(__name__)


class History:
    """
        History is list of History.Events which is automatically stores in dialog_context

        Example:
            Add history:

            h = History(dialog.dialog_context)
            ...
            h.append('booking', dialog_form, 'ask_master')

            Get last history event
            h = History(dialog.dialog_context)
            h.last()
    """

    class Event:
        """
            Represents history event
        """

        def __init__(self, name, form=None, priorities=None, render=None, timestamp=None):
            self.name = name
            self.form = form
            self.priorities = priorities
            self.render = render
            self.timestamp = timestamp if timestamp else int(round(time.time() * 1000))

        def to_dict(self):
            """
            Get event converted to dict
            """
            form_dict = self.form.serialize() if self.form else {}
            return {
                'name': self.name,
                'form': form_dict,
                'priorities': self.priorities,
                'timestamp': self.timestamp,
                'render': self.render
            }

        def __str__(self):
            return "History event: name %s, form: %s, priorities: %s, render: %s, timestamp: %s" % (
                self.name, self.form, self.priorities, self.render, self.timestamp)

    def __init__(self, raw_history,
                 read_only=False,
                 on_save=lambda *args, **kwargs: None,
                 parse=lambda e: e.__dict__):
        self.__read_only = read_only
        self.__raw_history = raw_history
        self.__events = self.__from_json(parse(raw_history))
        self.__on_save = on_save

    def append(self, name, form, priorities, render=None):
        """
        Append form to history
        Parameters:
        name (string): name of form or intent
        form (DialogForm): form after handling
        render (string): result of handling
        """

        if self.__read_only:
            raise Exception("Cannot modify read-only history")

        event = History.Event(name, form, priorities, render)
        LOG.info("New event added to history %s" % event)
        self.__events.append(event)
        self.__save()

    def __save(self):
        self.__on_save(self, self.__raw_history)

    def first(self):
        """
        Get first event from history
        """
        return self.__events[0] if len(self.__events) > 0 else None

    def last(self):
        """
        Get last event from history
        """
        return self.__events[-1] if len(self.__events) > 0 else None

    def group_by_name(self, name, reverse=False):
        """
        Get all events with the same name grouped and sorted
        """
        filtered = [event for event in self.__events if event.name == name]
        filtered = sorted(filtered, key=lambda e: e.timestamp, reverse=reverse)
        return filtered

    def by_name(self, name):
        """
        Get last event by name
        """
        filtered = self.group_by_name(name)
        return filtered[-1] if len(filtered) > 0 else None

    def all(self):
        """
        Get whole list of history events
        Try to not use this one
        """
        return self.__events

    def iter_from_begin_by_name(self, name):
        """
        Iterate over historical events grouped byname started from begin
        """
        return self.group_by_name(name)

    def iter_from_end_by_name(self, name):
        """
        Iterate over historical events grouped byname started from end
        """
        return self.group_by_name(name, True)

    def iter_from_end(self):
        """
        Iterate over history started from end
        """
        return sorted(self.__events, key=lambda e: e.timestamp, reverse=True)

    def iter_from_begin(self):
        """
        Iterate over history started from begin
        """
        return sorted(self.__events, key=lambda e: e.timestamp)

    def to_json(self):
        """
        Serialize to json
        """
        return [event.to_dict() for event in self.__events]

    @staticmethod
    def __from_json(json_data):
        """
        Deserialize from json
        """
        def to_history_event(json_event):
            if 'timestamp' in json_event and 'name' in json_event:
                form = DialogForm.get_form(json_event['form'])\
                    if 'form' in json_event and json_event['form']\
                    else None

                event = History.Event(name=json_event['name'],
                                      form=form,
                                      priorities=json_event.get('priorities'),
                                      render=json_event.get('render', None),
                                      timestamp=json_event['timestamp'])
                return event
            LOG.warning("Unhandled event was stored: %s" % json_event)

        result = []
        if json_data:
            result = [to_history_event(json_event) for json_event in json_data]
            result = sorted(result, key=lambda e: e.timestamp)
        return result


class HistoryManager:

    """
    dialog_contexts must be ordered by 'modify' timestamp
    """
    def __init__(self, young_history, old_history=None,
                 on_save=lambda *args, **kwargs: None,
                 parse=lambda e: e.__dict__):
        self.__young = History(young_history, on_save=on_save, parse=parse)
        self.__old = History(old_history, read_only=True, on_save=on_save, parse=parse) if old_history else None

    @property
    def young(self):
        return self.__young

    @property
    def old(self):
        return self.__old

    def append(self, name, form, priorities, render=None):
        self.young.append(name, form, priorities, render)

    def first(self):
        return self.young.first()

    def last(self):
        return self.young.last()

    def group_by_name(self, name, reverse=False):
        return self.young.group_by_name(name, reverse)

    def by_name(self, name):
        return self.young.by_name(name)

    def all(self):
        return self.young.all()

    def iter_from_begin_by_name(self, name):
        return self.young.iter_from_begin_by_name(name)

    def iter_from_end_by_name(self, name):
        return self.young.iter_from_end_by_name(name)

    def iter_from_end(self):
        return self.young.iter_from_end()

    def iter_from_begin(self):
        return self.young.iter_from_begin()
