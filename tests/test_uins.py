from app.utils import parse_uins


def test_parse_uins():
    assert parse_uins('123 234 345') == ['123', '234', '345']
    assert parse_uins('123\n234\n345') == ['123', '234', '345']
    assert parse_uins('123 \n234dsfs\n345!@#') == ['123', '234', '345']
    assert parse_uins('123\n234\n345\n \n \n') == ['123', '234', '345']
