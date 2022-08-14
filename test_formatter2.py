import pytest

from pathlib import Path

import sf_flags
from formatter2 import do_format


# pytest magic
def setup_module():
    sf_flags.reset_to_defaults()


test_inputs = []
expected_outputs = []
test_ids = []
for input_path in Path("queries_for_test").glob("*_IN.sql"):
    input_contents = input_path.read_text("utf-8").rstrip("\n")
    test_inputs.append(input_contents)

    output_path = input_path.with_name(input_path.name.replace("_IN.sql", "_OUT.sql"))
    output_contents = output_path.read_text("utf-8").rstrip("\n")
    expected_outputs.append(output_contents)

    test_id = input_path.name.replace("_IN.sql", "")
    test_ids.append(test_id)


@pytest.mark.parametrize("test_input,expected_output", zip(test_inputs, expected_outputs), ids=test_ids)
def test_do_format(test_input, expected_output):
    actual_output = do_format(test_input).render(indent=0)
    print(actual_output)
    #print(actual_output.replace(" ", "⦁"))
    assert expected_output == actual_output
