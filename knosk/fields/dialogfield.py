from typing import List, Any
from knosk.fields import FieldValue, DialogFieldValue
from knosk.choosers import Chooser
from knosk.suggesters import Suggester
from knosk.core import serializer
import logging

LOG = logging.getLogger(__name__)


class OverrideField:
    """
    It's the container for override parameters for the field
    it use in case of if need to override some of the field params
    :source is used for field identifications
    """

    def __init__(
            self,
            source: str = None,
            suggesters: List[Suggester] = None,
            choosers: List[Chooser] = None,
            exclude: DialogFieldValue = None):
        self._source = source
        self._suggesters = suggesters
        self._choosers = choosers
        self._exclude = exclude


class DialogField:

    def __init__(
            self,
            source: Any = None,
            matcher=None,
            suggesters: List[Suggester] = None,
            choosers: List[Chooser] = None,
            exclude: DialogFieldValue = None):
        self._source = source
        self._matcher = matcher
        self._suggesters = suggesters if suggesters else []
        self._choosers = choosers if choosers else []
        self.__origin = FieldValue.empty()
        self.__matched = FieldValue.empty()
        self.__suggested = FieldValue.empty()
        self._exclude = exclude  # exclude is specially may be None

    def match(self, form):
        LOG.info("Match field %s with value %s" % (self._source, self.__origin))
        if self._matcher:
            if not FieldValue.is_empty(self.__origin):
                matched_value = self._matcher(self.__origin, form)
                self._validate_match(matched_value)
                self.__matched = FieldValue.create(matched_value)
                LOG.info("Matched value for field %s is %s(%s)" % (self._source, self.__matched.__class__.__name__ ,self.__matched))

    def _validate_match(self, value):
        if isinstance(value, list) and len(value) > 1:
            raise ValueError("Expected single matched value")

    def _choose(self, value) -> DialogFieldValue:
        for chooser in self._choosers:
            chooser_name = chooser.__class__.__name__
            choosed_value = chooser(value)
            if choosed_value and len(choosed_value) < len(value):
                LOG.info("%s -> Choosed value is %s" % (chooser_name, choosed_value))
                return choosed_value

    def suggest(self, form) -> DialogFieldValue:
        LOG.info("Suggest field %s" % self._source)
        for suggester in self._suggesters:
            suggester_name = suggester.__class__.__name__
            suggester_result = suggester(self, form)
            LOG.info("%s -> Suggested value for field %s is %s" %
                (suggester_name, self._source, suggester_result))
            if suggester_result:
                suggester_result_fieldvalue = self._to_suggest_fieldvalue(suggester_result)
                if FieldValue.is_suggested(suggester_result_fieldvalue):
                    choosers_result = self._choose(suggester_result)
                    result = suggester_result if not choosers_result else choosers_result
                    suggester_result_fieldvalue = self._to_suggest_fieldvalue(result)
                self.__suggested = suggester_result_fieldvalue
                LOG.info("Suggested FieldValue for field %s is %s" %
                    (self._source, self.__suggested.__class__.__name__))
                return self.__suggested
        LOG.info("Suggested value for field %s is empty" % self._source)
        return FieldValue.empty()

    def _to_suggest_fieldvalue(self, value):
        return FieldValue.create_suggested(value)

    @property
    def value(self):
        if not FieldValue.is_empty(self.__suggested):
            return self.__suggested
        elif not FieldValue.is_empty(self.__matched):
            return self.__matched
        else:
            return FieldValue.empty()

    def get_value(self):
        """
            This method return exact value of the field
        """
        return self.value.value

    @property
    def origin(self):
        return self.__origin

    @property
    def matched(self):
        return self.__matched

    @property
    def suggested(self):
        return self.__suggested

    @property
    def exclude(self):
        return self._exclude

    @property
    def source(self):
        return self._source

    def _fill_origin(self, raw_payload):
        self.__origin = FieldValue.create(raw_payload.get(self._source, None))

    def _apply_override(self, overrides: List[OverrideField]):
        field_overrides = [
            override for override in overrides if override._source == self._source]
        if field_overrides:
            for override in field_overrides:
                if override._suggesters:
                    self._suggesters = override._suggesters
                if override._choosers:
                    self._choosers = override._choosers
                if override._exclude:
                    self._exclude = override._exclude

    def _fill_field(
            self,
            new_field,
            raw_payload: dict,
            overrides: List[OverrideField] = None,
            skip_payload=False):
        new_field._source = self._source
        new_field._matcher = self._matcher
        new_field._suggesters = self._suggesters
        new_field._choosers = self._choosers
        new_field._exclude = self._exclude
        if not skip_payload:
            new_field._fill_origin(raw_payload)
        if overrides:
            new_field._apply_override(overrides)
        return new_field

    def create(
            self,
            raw_payload: dict,
            overrides: List[OverrideField] = None,
            skip_payload=False):
        """
            Create field instance
        """
        return self._fill_field(
            DialogField(),
            raw_payload,
            overrides,
            skip_payload)

    def serialize(self) -> dict:
        result = {}
        result['source'] = serializer.simple_serialize(self._source)
        result['origin'] = serializer.simple_serialize(self.__origin.value)
        result['matched'] = serializer.simple_serialize(self.__matched.value)
        result['suggested'] = serializer.simple_serialize(
            self.__suggested.value)
        if self._exclude:
            result['exclude'] = serializer.simple_serialize(
                self._exclude.value)
        return result

    def deserialize(self, data: dict):
        self._source = serializer.simple_deserialize(data['source'])
        self.__origin = FieldValue.create(
            serializer.simple_deserialize(
                data['origin']))
        self.__matched = FieldValue.create(
            serializer.simple_deserialize(data['matched']))
        self.__suggested = FieldValue.create(
            serializer.simple_deserialize(
                data['suggested']))
        if 'exclude' in data:
            self._exclude = FieldValue.create(
                serializer.simple_deserialize(data['exclude']))

    def __eq__(self, other):
        if other:
            return self.source == other.source
        return False


class GroupField(DialogField):

    def __init__(self, *args, **kwargs):
        super(GroupField, self).__init__(*args, **kwargs)
        self.__selected_field = None

    def match(self, form):
        """
        The logic is the following
        if there is matcher on the field and its match field then this field is main
        if there is not matched fields take first with data and use it as main field
        if there is not fields with data so then use just first field in the group
        """
        first_with_origin = None
        for field in self.__fields():
            if not FieldValue.is_empty(field.origin):
                if not first_with_origin:
                    first_with_origin = field
                field.match(form)
                if not FieldValue.is_empty(field.matched):
                    self.__selected_field = field
                    return
        if first_with_origin:
            self.__selected_field = first_with_origin
        elif len(self.__fields()) > 0:
            self.__selected_field = self.__fields()[0]

    def suggest(self, form) -> DialogFieldValue:
        if self.__selected_field:
            return self.__selected_field.suggest(form)
        return FieldValue.empty()

    @property
    def value(self):
        if self.__selected_field:
            return self.__selected_field.value
        return FieldValue.empty()

    @property
    def origin(self):
        if self.__selected_field:
            return self.__selected_field.origin
        return FieldValue.empty()

    @property
    def matched(self):
        if self.__selected_field:
            return self.__selected_field.matched
        return FieldValue.empty()

    @property
    def suggested(self):
        if self.__selected_field:
            return self.__selected_field.suggested
        return FieldValue.empty()

    @property
    def source(self):
        if self.__selected_field:
            return self.__selected_field.source
        return None

    def get_value(self):
        if self.__selected_field:
            return self.__selected_field.get_value()

    def __fields(self):
        return self._source

    def create(
            self,
            raw_payload: dict,
            overrides: List[OverrideField] = None,
            skip_payload=False):
        """
        Get :field_definition copy and init origin in new field
        """
        fields = [
            field.create(
                raw_payload,
                overrides,
                skip_payload) for field in self.__fields()]
        new_field = GroupField(
            source=fields,
            matcher=self._matcher,
            suggesters=self._suggesters,
            choosers=self._choosers,
            exclude=self._exclude)
        return new_field

    def serialize(self) -> dict:
        result = {}
        if self.__selected_field:
            result['selected_field'] = serializer.simple_serialize(
                self.__selected_field._source)
            result.update(self.__selected_field.serialize())
        return result

    def deserialize(self, data: dict):
        if 'selected_field' in data:
            selected_fields = [field for field in self.__fields(
            ) if field._source == data['selected_field']]
            if selected_fields:
                self.__selected_field = selected_fields[0]
                self.__selected_field.deserialize(data)

    def __eq__(self, other):
        if self.__selected_field:
            return self.__selected_field == other
        return False


class ListField(DialogField):

    def __init__(self, *args, **kwargs):
        super(ListField, self).__init__(*args, **kwargs)

    def _validate_match(self, value):
        """
            if it's list do nothing
        """
        pass

    def _to_suggest_fieldvalue(self, value):
        if FieldValue.is_empty(self.origin):
            return super(ListField, self)._to_suggest_fieldvalue(value)
        return FieldValue.create(value)

    def create(
            self,
            raw_payload: dict,
            overrides: List[OverrideField] = None,
            skip_payload=False) -> DialogField:
        return self._fill_field(
            ListField(),
            raw_payload,
            overrides,
            skip_payload)


class OptionalField(DialogField):

    def __init__(self, *args, **kwargs):
        super(OptionalField, self).__init__(*args, **kwargs)

    def create(
            self,
            raw_payload: dict,
            overrides: List[OverrideField] = None,
            skip_payload=False) -> DialogField:

        return self._fill_field(
            OptionalField(),
            raw_payload,
            overrides,
            skip_payload)
