import pytest
from app import calc

class TestStringToNumber:

    def test_should_handle_floating_point(self):
        v = 1.0
        r = calc.string_to_number(v)
        assert v == r

    def test_should_convert_string_to_number(self):
        v = '33.4'
        r = calc.string_to_number(v)
        assert r == float(v)

    @pytest.mark.parametrize("val", [None,'text','UPPERCASE'])
    def test_should_fail_unconvertable(self, val):
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            _ = calc.string_to_number(val)
