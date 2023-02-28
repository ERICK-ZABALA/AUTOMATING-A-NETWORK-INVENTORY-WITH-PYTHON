from .kleenex_parser import KleenexParser
from .raw_parser import RawParser
from .robot_parser import RobotParser
from .xml_parser import TRADeXMLResultParser
from .xunit_parser import XunitParser
from .yaml_parser import YamlResultParser
from .base_parser import BaseResultsParser

from collections import OrderedDict

JSON_FILE = 'results.json'
YAML_FILE = 'results.yaml'
TRADE_XML = 'ResultsDetails.xml'


FILE2PARSER = OrderedDict([
    (JSON_FILE, YamlResultParser),
    (YAML_FILE, YamlResultParser),
    (TRADE_XML, TRADeXMLResultParser),
    ('CleanResultsDetails.yaml', KleenexParser),
    ('xunit.xml', XunitParser),
    ('output.xml', RobotParser)
])
