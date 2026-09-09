# dots-code-generator

# Usage
Add path with config_txt.py and path to "dots" python module to PYTHONPATH.

Call dcg.py:
cd examples
mkdir -p out
../bin/dcg.py -T templates -C config_txt -o out some_types.dots -v

Generated files will be places in directory "out".

Both `instance_ref` and `instance_ref<TypeName>` are supported, including
inside vectors and as key properties. The typed form targets a struct; locally
declared enums and built-in types are rejected as targets. External target names
are resolved by the target compiler, since the generator does not load imported
schemas.

Target configurations map the generic form through `type_mapping["instance_ref"]`
and can set `instance_ref_format = "TypedRef<{}>"` for typed references. The
default typed format is `instance_ref<{}>`. The target name is preserved, and
generated imports include that target (except for self-references). Existing
configurations need no new setting. For example:

```
struct Status {
    1: [key] instance_ref subject;
    2: instance_ref<ExampleType> example;
    3: vector<instance_ref<ExampleType>> examples;
}
```

The template attributes `type` and `vector_type` retain the wire descriptor
spellings, while `cxx_type` and `cxx_vector_type` contain configured target types.
`keys` and `keyAttributes` retain declaration order for compatibility; templates
that use them for canonical identities must sort key attributes by `tag`.
Reference value validation and deterministic CBOR encoding are runtime concerns.


# Update DOTS grammar

DOTS grammer is defined in "dots.lark". If the grammar is updated, a new
parser has to be generated with the "lark" python module:

python -m lark.tools.standalone dots.lark --maybe_placeholders -o dots/dots_parser.py
