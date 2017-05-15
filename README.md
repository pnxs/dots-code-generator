# dots-code-generator

# Usage
Add path with config_txt.py and path to "dots" python module to PYTHONPATH.

Call dcg.py:
cd examples
mkdir -p out
../bin/dcg.py -T templates -C config_txt -o out some_types.dots -v

Generated files will be places in directory "out".
