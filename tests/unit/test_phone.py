import pytest
from backend.utils.phone import format_br_phone


@pytest.mark.parametrize(
    "raw,expected_display,expected_e164",
    [
        ("", "Telefone não informado", None),  # vazio
        ("1130456789", "+55 (11) 3045-6789", "+551130456789"),  # 10 dígitos (fixo)
        ("11987654321", "+55 (11) 98765-4321", "+5511987654321"),  # 11 dígitos (celular)
        ("(11) 9 8765-4321", "+55 (11) 98765-4321", "+5511987654321"),  # já formatado
        ("12345", "Telefone não informado", None),  # curto/ruim
    ],
)
def test_format_br_phone(raw, expected_display, expected_e164):
    display, e164 = format_br_phone(raw)
    assert display == expected_display
    assert e164 == expected_e164
