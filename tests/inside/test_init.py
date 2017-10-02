from c2corg_images import parse_resizing_config, RESIZING_CONFIG

import json


def test_resizing_config_from_environment():
    resizing_config = [
        {'suffix': 'master', 'convert': ['-resize', '2048x2048>', '-quality', '90']},
        {'suffix': 'L', 'convert': ['-resize', '780x487>', '-quality', '90']},
        {'suffix': 'M', 'convert': ['-resize', '268x168>', '-quality', '90']},
        {'suffix': 'S', 'convert': ['-resize', '170x106>', '-quality', '90']},
        {'suffix': 'XS', 'convert': ['-resize', '78x78>', '-quality', '90']}
    ]
    serialized = json.dumps(resizing_config)
    parsed = parse_resizing_config(serialized)
    assert parsed == resizing_config


def test_resizing_config_from_default():
    parsed = parse_resizing_config(None)
    assert parsed == RESIZING_CONFIG
