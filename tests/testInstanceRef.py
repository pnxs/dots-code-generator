import tempfile
import unittest
from pathlib import Path

from lark import Lark, Token, Tree

from bin.dcg import DotsCodeGenerator
from dots import DdlParser, DotsTransformer
from dots.dots_parser import Token as StandaloneToken, Tree as StandaloneTree, UnexpectedInput


class TestInstanceRef(unittest.TestCase):
    def test_reference_types_and_mapping(self):
        source = """
            import Target
            struct Links {
                3: [key] instance_ref subject;
                1: [key] instance_ref<Target> target;
                4: vector<instance_ref> subjects;
                5: vector<instance_ref<Target>> targets;
                6: vector<vector<instance_ref<Target>>> nested;
                7: string label;
            }
        """
        parser = DdlParser()
        parser.ddlconfig.update({
            "type_mapping": {"instance_ref": "GenericRef", "string": "Text"},
            "instance_ref_format": "TypedRef<{}>",
            "vector_format": "List<{}>",
        })
        result = parser.parse(source)
        attrs = result["structs"][0]["attributes"]
        self.assertEqual([a["type"] for a in attrs], [
            "instance_ref", "instance_ref<Target>", "vector<instance_ref>",
            "vector<instance_ref<Target>>", "vector<vector<instance_ref<Target>>>",
            "string",
        ])
        self.assertEqual([a["cxx_type"] for a in attrs], [
            "GenericRef", "TypedRef<Target>", "List<GenericRef>",
            "List<TypedRef<Target>>", "List<List<TypedRef<Target>>>", "Text",
        ])
        self.assertEqual(attrs[3]["cxx_vector_type"], "TypedRef<Target>")
        self.assertFalse(attrs[-1]["vector"])
        self.assertEqual(result["structs"][0]["keys"], ["subject", "target"])
        # Keep the source grammar and shipped standalone parser in agreement.
        grammar = Path(__file__).resolve().parents[1] / "dots.lark"
        tree = Lark(grammar.read_text(), parser="lalr", maybe_placeholders=True).parse(source)
        # The standalone transformer uses its own Tree and Token classes.
        def standalone(node):
            if isinstance(node, Tree):
                return StandaloneTree(node.data, [standalone(child) for child in node.children])
            if isinstance(node, Token):
                return StandaloneToken(node.type, node.value)
            return node

        self.assertEqual(DotsTransformer(parser.ddlconfig).transform(standalone(tree)), result)

    def test_default_and_legacy_configuration(self):
        parser = DdlParser()
        del parser.ddlconfig["instance_ref_format"]
        attrs = parser.parse("struct S { 1: instance_ref r; 2: instance_ref<T> t; 3: vector<instance_ref<T>> refs; }")["structs"][0]["attributes"]
        self.assertEqual([a["cxx_type"] for a in attrs],
                         ["instance_ref", "instance_ref<T>", "dots::Vector<instance_ref<T>>"])

    def test_forward_self_and_keyless_targets(self):
        result = DdlParser().parse("""
            struct First { 1: instance_ref<Second> other; 2: instance_ref<First> self; }
            struct Second { 1: string value; }
        """)
        self.assertEqual(len(result["structs"]), 2)

    def test_non_struct_targets(self):
        for target in ("int32", "string", "any", "instance_ref", "uuid", "E"):
            with self.subTest(target=target):
                with self.assertRaisesRegex(ValueError, "target must be a struct"):
                    DdlParser().parse(
                        "struct S { 1: vector<instance_ref<" + target + ">> ref; } enum E { 1: item }"
                    )

    def test_invalid_type_arguments(self):
        for target in ("", "vector<string>", "instance_ref<T>", "T,U"):
            with self.subTest(target=target):
                with self.assertRaises(UnexpectedInput):
                    DdlParser().parse("struct S { 1: instance_ref<" + target + "> ref; }")

    def test_generator_configuration_and_imports(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            config = directory / "config_instance_ref_test.py"
            config.write_text('''
struct_templates = ["struct.txt.dotsT"]
enum_templates = []
vector_format = "List<{}>"
instance_ref_format = "Ref<{}>"
type_mapping = {"instance_ref": "GenericRef"}
''')
            (directory / "struct.txt.dotsT").write_text(
                '{{ imports | join(",") }}\n'
                '{% for attr in attributes %}{{ attr.type }}={{ attr.cxx_type }}\n{% endfor %}'
            )
            source = directory / "links.dots"
            source.write_text('''
                import Unused
                struct Links {
                    1: instance_ref generic;
                    2: vector<instance_ref<Target>> targets;
                    3: instance_ref<Links> self;
                }
            ''')
            generator = DotsCodeGenerator()
            generator.load_config(str(config))
            generator.template_path = tmp
            generator.output_path = tmp
            generator.process_file(str(source))
            self.assertEqual((directory / "Links.txt").read_text(),
                             "Target\ninstance_ref=GenericRef\n"
                             "vector<instance_ref<Target>>=List<Ref<Target>>\n"
                             "instance_ref<Links>=Ref<Links>\n")


if __name__ == "__main__":
    unittest.main()
