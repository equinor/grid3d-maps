"""Loading nested config files"""

import io
import logging
import os.path

import yaml
from yaml.constructor import ConstructorError
from yaml.nodes import MappingNode

file_types = (io.IOBase,)


logger = logging.getLogger(__name__)


class FMUYamlSafeLoader(yaml.SafeLoader):
    """Class for making it possible to use nested YAML files.

    Code is borrowed from David Hall (but extended later):
    https://davidchall.github.io/yaml-includes.html
    """

    # pylint: disable=too-many-ancestors

    def __init__(self, stream):
        self._root = os.path.split(stream.name)[0]
        super().__init__(stream)

        FMUYamlSafeLoader.add_constructor(
            yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
            FMUYamlSafeLoader.construct_mapping,
        )

        FMUYamlSafeLoader.add_constructor("!include", FMUYamlSafeLoader.include)
        FMUYamlSafeLoader.add_constructor("!import", FMUYamlSafeLoader.include)
        FMUYamlSafeLoader.add_constructor(
            "!include_from", FMUYamlSafeLoader.include_from
        )
        # if root:
        #     self.root = root
        # elif isinstance(self.stream, file_types):
        #     self.root = os.path.dirname(self.stream.name)
        # else:
        #     self.root = os.path.curdir

    def include(self, node):
        """Include method"""

        result = None
        if isinstance(node, yaml.ScalarNode):
            result = self.extract_file(self.construct_scalar(node))

        elif isinstance(node, yaml.SequenceNode):
            result = []
            for filename in self.construct_sequence(node):
                result += self.extract_file(filename)

        elif isinstance(node, yaml.MappingNode):
            result = {}
            for knum, val in self.construct_mapping(node).items():
                result[knum] = self.extract_file(val)

        else:
            print("Error:: unrecognised node type in !include statement")
            raise yaml.constructor.ConstructorError

        return result

    def include_from(self, node):
        """The include_from method, which parses parts of another YAML.

        E.g.
        dates: !include_from /private/jriv/tmp/global_config.yml::global.DATES
        diffdates: !include_from tests/yaml/global_config.yml::global.DIFFDATES

        In the first case, it will read the ['global']['DATES'] values

        The files must have full path (abs or relative)
        """

        result = None
        oldroot = self._root

        if isinstance(node, yaml.ScalarNode):
            filename, val = self.construct_scalar(node).split("::")
            with open(filename, "r") as fp:
                result = yaml.safe_load(fp)
            self._root = oldroot

            fields = val.strip().split(".")
            for ilev, field in enumerate(fields):
                if field in set(result.keys()):
                    logger.info("Level %s key, field name is %s", ilev + 1, field)
                    result = result[field]
                else:
                    logger.critical(
                        "Level %s key, field name not found %s", ilev + 1, field
                    )
                    raise yaml.constructor.ConstructorError

        else:
            print("Error:: unrecognised node type in !include_from statement")
            raise yaml.constructor.ConstructorError

        return result

    def extract_file(self, filename):
        """Extract file method"""

        filepath = os.path.join(self._root, filename)
        with open(filepath, "r") as yfile:
            return yaml.safe_load(yfile)

    # from https://gist.github.com/pypt/94d747fe5180851196eb
    def construct_mapping(self, node, deep=False):
        if not isinstance(node, MappingNode):
            raise ConstructorError(
                None,
                None,
                "Expected a mapping node, but found %s" % node.id,
                node.start_mark,
            )

        mapping = {}

        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            try:
                hash(key)
            except TypeError as exc:
                raise ConstructorError(
                    "While constructing a mapping",
                    node.start_mark,
                    "found unacceptable key (%s)" % exc,
                    key_node.start_mark,
                ) from exc
            # check for duplicate keys
            if key in mapping:
                raise ConstructorError(
                    "Found duplicate key <{}> ... {}".format(key, key_node.start_mark)
                )
            value = self.construct_object(value_node, deep=deep)
            mapping[key] = value
        return mapping
