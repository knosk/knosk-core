from typing import List, Dict
from bot.fields import OverrideField, DialogField, FieldValue, ListField, OptionalField
from bot import serializer
import json
import importlib
import logging
import copy

LOG = logging.getLogger(__name__)


class DialogForm:
    class FormException(RuntimeError):
        """Throw to indicate invalid condition occured during form handling (match, suggest).
        Optional parameters are useful to pass context of condition.
        Cause is used to properly handle exception up on the stack.
        This should be name of rendering template."""

        def __init__(self, cause, **params):
            self.cause = cause
            self.params = params

    class WrongInputException(FormException):
        """
            When there is some wrong input from user show this exception
        """
        pass

    class ValidationException(FormException):
        """
            When invalid combination was found
        """
        pass

    def __init__(self,
                 payload: Dict[str,
                               str] = None,
                 overrides: List[OverrideField] = None,
                 clean_field_data: str = None,
                 history=None,
                 **kwargs):
        self.__payload = {} if not payload else payload
        self.__overrides = [] if not overrides else overrides
        self._fields = {}
        self.history = history
        if self.__payload:  # if payload is None that means that form was instantiated for deserialization
            self.__dict__.update(kwargs)
            self._build_fields(payload, overrides, clean_field_data)

    def _build_fields(
            self,
            payload: dict,
            overrides: List[OverrideField],
            clean_field_data: str = None):
        field_defs = {}
        if 'Meta' in dir(self):
            if 'fields' in dir(self.Meta):
                field_defs = {
                    field_name: getattr(self, field_name) for field_name in self.Meta.fields
                }
        for field_name, field_def in field_defs.items():
            need_skip_payload = clean_field_data == field_name
            LOG.info("Rebuild field %s-%s-%s" %
                     (field_name, need_skip_payload, payload))
            self._fields[field_name] = field_def.create(
                payload,
                overrides=overrides,
                skip_payload=need_skip_payload)

    def clone(self):
        return copy.deepcopy(self)

    def match(self):
        LOG.info("==== Start matching form %s ====" % self.__class__.__name__)
        for field in self._fields.values():
            field.match(self)
        LOG.info("==== End matching form %s ====" % self.__class__.__name__)

    @property
    def payload(self):
        return self.__payload

    def suggest(self) -> (str, DialogField):
        LOG.info("==== Start suggesting form %s ====" % self.__class__.__name__)
        for field_name, field in self._fields.items():
            is_optional_field = isinstance(field, OptionalField)

            if FieldValue.is_empty(field.origin) and is_optional_field:
                LOG.info("Skipping empty optional field {}".format(field_name))
                # skipping optional field suggest
                continue

            suggested_result = field.suggest(self)

            if FieldValue.is_empty(suggested_result)\
                    or FieldValue.is_suggested(suggested_result):
                LOG.info("==== End suggesting form %s ====" % self.__class__.__name__)
                return field_name, field
        LOG.info("==== End suggesting form %s ====" % self.__class__.__name__)
        return None

    def handle(self, **kwargs):
        """
            Just wrapper for form logic call: match->suggest->validate
        """
        self.match()
        suggest_result = self.suggest()
        if suggest_result:
            field_name, field = suggest_result
            self.validate_field(field_name, field)
            return suggest_result
        self.validate(**kwargs)

    def get_exclude(self, field_name) -> FieldValue:
        """
            For internal needs exclude could be None, but for external needs everything should be FieldValue
        """
        exclude = self._fields[field_name].exclude
        if not exclude:
            return FieldValue.empty()
        return exclude

    def get(self, field_name: str) -> DialogField:
        return self._fields[field_name]

    def has(self, field_name: str) -> bool:
        return field_name in self._fields

    def clean_field_data(self, field_name: str, overrides: List = None):
        """
            Rebuild whole form that mean that all form field data will be removed(all suggests and matches)
            and fields will be reacreated with data from payload except :field_name.
            Payload data for :field_name will be hidden during rebuild
        """
        if overrides:
            self.__overrides = self.__overrides + overrides
        self._build_fields(self.__payload, self.__overrides, field_name)

    def get_field_names(self):
        return list(self._fields.keys())

    def get_field_name(self, lookup_field):
        field_names = [
            fname for fname,
            field in self._fields.items() if field == lookup_field]
        if field_names:
            return field_names[0]
        return None

    def validate(self, **kwargs):
        for (fname, field) in self._fields.items():
            self.validate_field(fname, field)

        self.validate_form(**kwargs)

    def validate_field(self, fname: str, field: DialogField):
        """
        Run validator that validate state of form
        SHOULD be overridden
        """
        pass

    def validate_form(self):
        """
        Run validator that validate state of form
        SHOULD be overrided
        """
        raise NotImplemented("It should be implemented in your form")

    def suggest_by_field(self, fname):
        field = self._fields[fname]
        return field.suggest(self)

    def serialize(self) -> dict:
        result = {}
        result["name"] = "%s.%s" % (self.__module__, self.__class__.__name__)
        result['payload'] = serializer.serialize(self.__payload)
        result['fields'] = {field_name: field.serialize()
                            for field_name, field in self._fields.items()}
        return result

    def deserialize(self, data):
        self.__payload = serializer.deserialize(data['payload'])
        self._build_fields(self.__payload, [])
        for field_name, field in self._fields.items():
            field_data = data['fields'].get(field_name, None)
            if field_data:
                field.deserialize(field_data)

    @classmethod
    def get_form(cls, data):
        form_name = data['name']
        module_name, class_name = form_name.rsplit(".", 1)
        FormClass = getattr(importlib.import_module(module_name), class_name)
        form = FormClass()
        form.deserialize(data)
        return form

    def to_dict(self):
        return {
            fname: field.value.value for fname,
            field in self._fields.items()}

    def __str__(self):
        return "%s" % self.to_dict()
