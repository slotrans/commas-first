import pytest

from pathlib import Path

import sf_flags
from formatter2 import do_format


# pytest magic
def setup_module():
    sf_flags.reset_to_defaults()


BASE_DIRECTORY = "queries_for_test"


test_inputs = []
expected_outputs = {
    "trim_leading_whitespace__off": [],
    "trim_leading_whitespace__on": [],
}
test_ids = []
for input_path in Path(BASE_DIRECTORY).glob("*_IN.sql"):
    input_contents = input_path.read_text("utf-8").rstrip("\n")
    test_inputs.append(input_contents)

    output_name = input_path.name.replace("_IN.sql", "_OUT.sql")
    for variation in expected_outputs.keys():
        output_path = Path(BASE_DIRECTORY) / variation / output_name
        output_contents = output_path.read_text("utf-8").rstrip("\n")
        expected_outputs[variation].append(output_contents)

    test_id = input_path.name.replace("_IN.sql", "")
    test_ids.append(test_id)


@pytest.mark.parametrize("test_input,expected_output", zip(test_inputs, expected_outputs["trim_leading_whitespace__off"]), ids=test_ids)
def test_do_format_with_trim_leading_whitespace_off(test_input, expected_output):
    sf_flags.TRIM_LEADING_WHITESPACE = False
    actual_output = do_format(test_input)
    print(actual_output)
    #print(actual_output.replace(" ", "⦁"))
    assert expected_output == actual_output


@pytest.mark.parametrize("test_input,expected_output", zip(test_inputs, expected_outputs["trim_leading_whitespace__on"]), ids=test_ids)
def test_do_format_with_trim_leading_whitespace_on(test_input, expected_output):
    sf_flags.TRIM_LEADING_WHITESPACE = True
    actual_output = do_format(test_input)
    print(actual_output)
    #print(actual_output.replace(" ", "⦁"))
    assert expected_output == actual_output
