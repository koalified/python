import yaml
import json
import xxhash
import requests
from koalified import types
from koalified.compile import to_python


class Schema(object):

    def __init__(self, uri=None, text=None, supported_types=types.built_in, fail_fast=True, allow_imports=True,
                 score_fields=False, explain=False, precompile=False):
        self.supported_types = supported_types
        self.definition = self._load_definition(uri=uri, text=text, allow_imports=allow_imports)
        self.metadata = self.definition.pop('__metadata__', {})
        self.version = self.metadata['schema_version']
        self.fail_fast = fail_fast
        self.score_fields = score_fields
        self.explain = explain
        if precompile:
            self._compiled = to_python(self)
        else:
            self._compiled = False

    def _add_imports(self, definition):
        for field, value in definition.items():
            if type(value) == dict:
                self._add_imports(value)
            elif type(value) == list:
                for index, nested_value in enumerate(value):
                    if type(nested_value) == dict:
                        self._add_imports(nested_value)
                    elif type(nested_value) == str and nested_value.startswith('&'):
                        value[index] = self._load_definition(nested_value[1:])
            elif type(value) == str and value.startswith('&'):
                definition[field] = self._load_definition(value[1:])

        extend = definition.pop('@', None)
        if extend:
            definition = self._load_definition(extend).update(definition)

        return definition

    def _load_definition(self, uri=None, text=None, allow_imports=True):
        if not uri and not text:
            raise ValueError("A schema uri or text must be defined")
        elif uri and text:
            raise ValueError("You cannot specify multiple sources. Choose one: uri or text.")

        if uri:
            if uri.startswith('http'):
                text = requests.get(uri).content
            else:
                with open(uri.lstrip('file://')) as schema_file:
                    text = schema_file.read()

        definition = yaml.safe_load(text)
        if allow_imports:
            self._add_imports(definition)

        metadata = definition.setdefault('__metadata__', {})
        if not metadata.get('schema_version', None):
            metadata['schema_version'] = xxhash.xxh32(text).hexdigest()

        return definition

    def compiled(self):
        if not self._compiled:
            self._compiled = to_python(self)

        return self._compiled

    def __call__(self, data):
        return self.compiled()(data)
