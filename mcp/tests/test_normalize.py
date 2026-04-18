from cdmx_data.normalize import normalize_text, canonical_alcaldia, parse_date, parse_coord
from datetime import date


class TestNormalizeText:
    def test_lowercases(self):
        assert normalize_text("HOLA") == "hola"

    def test_removes_tildes(self):
        assert normalize_text("Cuauhtémoc") == "cuauhtemoc"

    def test_collapses_whitespace(self):
        assert normalize_text("  hola   mundo  ") == "hola mundo"

    def test_strips(self):
        assert normalize_text("  hola  ") == "hola"

    def test_n_tilde_preserved_as_n(self):
        assert normalize_text("Álvaro Obregón") == "alvaro obregon"


class TestCanonicalAlcaldia:
    def test_exact_match(self):
        assert canonical_alcaldia("Coyoacán") == "Coyoacán"

    def test_without_accent(self):
        assert canonical_alcaldia("Coyoacan") == "Coyoacán"

    def test_uppercase(self):
        assert canonical_alcaldia("COYOACÁN") == "Coyoacán"

    def test_cuauhtemoc_variants(self):
        assert canonical_alcaldia("Cuauhtémoc") == "Cuauhtémoc"
        assert canonical_alcaldia("Cuauhtemoc") == "Cuauhtémoc"
        assert canonical_alcaldia("CUAUHTÉMOC") == "Cuauhtémoc"

    def test_alvaro_obregon(self):
        assert canonical_alcaldia("Alvaro Obregon") == "Álvaro Obregón"

    def test_unknown_returns_none(self):
        assert canonical_alcaldia("Ciudad Desconocida") is None

    def test_all_16_alcaldias(self):
        raw = [
            "Álvaro Obregón", "Azcapotzalco", "Benito Juárez", "Coyoacán",
            "Cuajimalpa de Morelos", "Cuauhtémoc", "Gustavo A. Madero", "Iztacalco",
            "Iztapalapa", "La Magdalena Contreras", "Miguel Hidalgo", "Milpa Alta",
            "Tláhuac", "Tlalpan", "Venustiano Carranza", "Xochimilco",
        ]
        for a in raw:
            assert canonical_alcaldia(a) == a, f"Falló: {a}"


class TestParseDate:
    def test_iso_format(self):
        assert parse_date("2024-01-15") == date(2024, 1, 15)

    def test_slash_format(self):
        assert parse_date("15/01/2024") == date(2024, 1, 15)

    def test_iso_with_time(self):
        assert parse_date("2024-01-15T10:30:00") == date(2024, 1, 15)

    def test_returns_date_object(self):
        result = parse_date("2024-06-01")
        assert isinstance(result, date)

    def test_slash_format_is_dd_mm_not_mm_dd(self):
        # 03/02/2024 debe ser 3 de febrero, no 2 de marzo
        assert parse_date("03/02/2024") == date(2024, 2, 3)


class TestParseCoord:
    def test_dot_decimal(self):
        assert parse_coord("19.4326") == 19.4326

    def test_comma_decimal(self):
        assert parse_coord("19,4326") == 19.4326

    def test_float_passthrough(self):
        assert parse_coord(19.4326) == 19.4326

    def test_int_passthrough(self):
        assert parse_coord(19) == 19.0

    def test_negative(self):
        assert parse_coord("-99,1332") == -99.1332
