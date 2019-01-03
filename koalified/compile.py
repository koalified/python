import copy
from collections import namedtuple

try:
    import Cython
except ImportError:
    Cython = False

construct = namedtuple('Construct', ['name', 'compute_quality', 'weight', 'required', 'multiple', 'mutate'])
validator = namedtuple('Validator', ['construct', 'args', 'kwargs'])
INDENT = ' ' * 4


def to_python(schema):
    definition = copy.deepcopy(schema.definition)
    metadata = schema.definition.pop('__metadata__', {})
    code = _compile_schema(schema)
    if Cython and hasattr(Cython, 'inline'):
        name_space = schema.supported_types.copy()
        name_space['metadata'] = schema.metadata
        name_space = Cython.inline(code, name_space)
    else:
        name_space = schema.supported_types.copy()
        name_space['metadata'] = schema.metadata
        exec(compile(code, '<string>', 'exec'), name_space)
    return name_space['apply_schema']


def _indent(code):
    return [INDENT + statement for statement in code]


def _read_construct(line):
    if '~' in line:
        split_line = line.split('~', -1)
        weight = split_line.pop(-1)
        try:
            weight = float(weight)
        except ValueError:
            raise ValueError('Weight must be a float value not "{}"'.format(weight))
        line = '~'.join(split_line)
    else:
        weight = 1

    required = False
    compute_quality = True
    multiple = False
    mutate = False
    index = 0
    for index, character in enumerate(line[::-1]):
        if character == '!':
            if required:
                raise ValueError('You cannot set required twice!')
            required = True
        elif character == '?':
            if not compute_quality:
                raise ValueError('You cannot unset quality computations twice!')
            elif weight != 1:
                raise ValueError('You cannot set a quality weight but then specify to skip quality')
            compute_quality = False
            weight = 0
        elif character == '+':
            if multiple:
                raise ValueError('You cannot set multiple twice!')
            multiple = True
        elif character == '=':
            if mutate:
                raise ValueError('You cannot set mutate twice!')
            mutate = True
        elif character == '|':
            index += 1
            break
        else:
            break

    return construct(line[:-index] if index else line, compute_quality, weight, required, multiple, mutate)


def _start(code, counter):
    code.append('input{} = input'.format(counter))
    code.append('output{} = output'.format(counter))


def _end(code, counter):
    code.append('output = output{}'.format(counter))
    code.append('input = input{}'.format(counter))


def _compile_schema(schema):
    code = ['def apply_schema(full_input):',
            '    score = 0',
            '    possible_score = 0',
            '    input = full_input',
            '    output = full_output = {"__metadata__": metadata.copy()}']
    if not schema.fail_fast:
        code.append('    errors = []')
    if schema.score_fields:
        code.append('    field_scores = {}')
        code.append('    full_output["__metadata__"]["field_scores"] = field_scores')
    if schema.explain:
        code.append('    reasons = []')
        code.append('    full_output["__metadata__"]["explain_scores"] = reasons')

    code.extend(_indent(_compile_fields(schema, schema.definition)))
    if not schema.fail_fast:
        code.append('    if errors:')
        code.append('        raise ValueError("Errors occurred when applying the schema: {}".format(",".join(errors)))')
    code.append('    full_output["__metadata__"]["score"] = score / possible_score')
    code.append('    return full_output')
    return '\n'.join(code)


def _compile_fields(schema, fields, counter=1, path=()):
    code = []
    field_names = []
    include_extra = False
    include_extra_validators = None
    for field, validators in fields.items():
        field = _read_construct(field)
        field_names.append(field.name)
        if field.name == '**':
            include_extra = field
            include_extra_validators = [validators] if type(validators) == str else validators
        elif type(validators) == dict:
            if field.multiple:
                _start(code, counter)
                code.append('output["{}"] = []'.format(field.name))
                code.append('input_list = input["{0}"]'.format(field.name))
                code.append('if type(input_list) == tuple:')
                code.append('    input_list = list(input_list)')
                code.append('elif type(input_list) is not list:')
                code.append('    input_list = [input_list]')
                code.append('output_list = output["{}"]'.format(field.name))
                code.append('for input in input_list:'.format(field.name))
                code.append('    output = {}')
                code.extend(_indent(_compile_fields(schema, validators, counter + 1, path + (field.name, ))))
                code.append('    if output:')
                code.append('        output_list.append(output)')
                if field.required:
                    code.append('if not output_list:')
                    if schema.fail_fast:
                        code.append('    raise ValueError("At least one {} is required")'.format(field.name))
                    else:
                        code.append('    errors.append("At least one {} is required")'.format(field.name))
                _end(code, counter)
            else:
                _start(code, counter)
                code.append('input = input["{0}"]'.format(field.name))
                code.append('output["{}"] = {}'.format(field.name, '{}'))
                code.append('output = output["{}"]'.format(field.name))
                code.extend(_compile_fields(schema, validators, counter + 1, path + (field.name, )))
                _end(code, counter)
        else:
            code.extend(_compile_field(schema, field, validators, path=path))
    if include_extra:
        if include_extra.required or include_extra.multiple:
            raise ValueError('It is currently not supported to add any rules to the inclusion of extra fields')
        code.append('possible_validator_score = 1')
        code.append('validator_score = 1')
        code.append('for field, value in  [(field, value) for (field, value) in '
                    'input.items() if field not in {}]:'.format(repr(field_names)))
        code.append('    output_value = value')
        code.extend(_indent(_compile_validators(schema, field, include_extra_validators, path)))
        code.append('    if output_value is not None:')
        code.append('        output[field] = output_value')
        code.append('score += {} * (validator_score / possible_validator_score)'.format(include_extra.weight))
        code.append('possible_score += {}'.format(include_extra.weight))

    return code


def _compile_field(schema, field, validators, path):
    field_path = '.'.join(path + (field.name, ))
    validators = [validators] if type(validators) == str else validators

    exists_code = ['if not input.get("{}", None):'.format(field.name)]
    if field.required:
        if schema.fail_fast:
            exists_code.append('    raise ValueError("{}  required but not specified")'.format(field.name))
        else:
            exists_code.append('    errors.append(ValueError("{}  required but not specified"))'.format(field.name))
    else:
        exists_code.append('    possible_score += {}'.format(field.weight))
        if schema.score_fields:
            exists_code.append('    field_scores["{}"] = 0'.format(field_path))
        if field.weight and schema.explain:
            exists_code.append('    reasons.append("Value for {} was not given.")'.format(field_path))
    exists_code.extend(['else:',
                        '    output["{0}"] = input["{0}"]'.format(field.name)])

    if not validators:
        return exists_code

    code = ['possible_validator_score = 1',
            'validator_score = 1']

    if field.multiple:
        code.append('if type(output["{0}"]) == tuple:'.format(field.name))
        code.append('    output["{0}"] = list(output["{0}"])'.format(field.name))
        code.append('elif type(output["{0}"]) is not list:'.format(field.name))
        code.append('    output["{0}"] = [output["{0}"]]'.format(field.name))
        code.append('for index, output_value in enumerate(output["{0}"]):'.format(field.name))
        code.extend(_indent(_compile_validators(schema, field, validators, field_path)))
        code.append('if None in output["{0}"]:'.format(field.name))
        code.append('    output["{0}"] = [value for value in output["{0}"] if value is not None]'.format(field.name))
    else:
        code.append('output_value = output["{0}"]'.format(field.name))
        code.extend(_compile_validators(schema, field, validators, field_path))
        code.append('if output_value is not None:')
        code.append('    output["{0}"] = output_value'.format(field.name))
        code.append('else:')
        code.append('    output.pop("{0}")'.format(field.name))

    if schema.score_fields:
        code.append('field_scores["{}"] = (validator_score / possible_validator_score)'.format(field_path))

    code.append('score += {} * (validator_score / possible_validator_score)'.format(field.weight))
    code.append('possible_score += {}'.format(field.weight))
    return exists_code + _indent(code)


def _read_value(schema, value):
    if ':' in value:
        value, value_type = value.split(':')
        if not value_type in schema.supported_types:
            raise ValueError('provided type of "{}" not one of the support value types: {}'.format
                                (value_type, ', '.join(schema.supported_types.keys())))
        return schema.supported_types[value_type](value)

    return value


def _read_validator(schema, string):
    parts = string.split(' ')
    kind = _read_construct(parts.pop(0))

    args = []
    kwargs = {}
    for value in parts:
        if '=' in value:
            key, value = value.split('=')
            value = _read_value(schema, value)

            if key in kwargs:
                if kwargs[key] != list:
                    kwargs[key] = [kwargs[key]]
                kwargs[key].append(value)
            else:
                kwargs[key] = value
        else:
            args.append(_read_value(schema, value))

    return validator(kind, args, kwargs)


def _compile_validators(schema, field, validators, field_path):
    code = []
    for validator in validators:
        code.append('if output_value is not None:')
        validator = _read_validator(schema, validator)
        if validator.construct.weight:
            code.append('    possible_validator_score += {}'.format(validator.construct.weight))
        code.append('    try:')
        call_validator = '{}(output_value, *{}, **{})'.format(validator.construct.name, repr(validator.args),
                                                              repr(validator.kwargs))
        if validator.construct.mutate:
            code.append('        output_value = {}'.format(call_validator))
        else:
            code.append('        {}'.format(call_validator))
        if validator.construct.weight:
            code.append('        validator_score += {}'.format(validator.construct.weight))
        code.append('    except Exception as e:')
        if validator.construct.required:
            if field.required:
                if schema.fail_fast:
                    code.append('        raise e')
                else:
                    code.append('        errors.append(e)')
            else:
                code.append('        output_value = None')
                if schema.explain:
                    code.append('        reasons.append("Provided value "'
                                '                       " for {} field did not match required validator {} {} {}"'
                                '                      )'.format(field_path, validator.construct.name,
                                                             ' '.join(validator.args), str(validator.kwargs)))


        else:
            if schema.explain:
                code.append('        reasons.append("Provided value of " + str(output_value) +'
                            '                       " for {} field did not match {} {} {}"'
                            '                      )'.format(field_path, validator.construct.name,
                                                             ' '.join(validator.args), str(validator.kwargs)))
            else:
                code.append('        pass')
    if field.multiple:
        code.append('output["{0}"][index] = output_value'.format(field.name))

    return code
