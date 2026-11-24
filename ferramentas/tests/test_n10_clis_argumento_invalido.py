"""N10: argumento inválido nas CLIs vira erro de uso (rc 2, mensagem curta), nunca traceback, e nada é gravado."""
import pytest

import temporada
from dossie import notas


@pytest.mark.parametrize("flag,valor", [("--trimestre", "5T26"), ("--trimestre", "4T26"), ("--trimestre", "abc"),
                                        ("--simular", "9T99"), ("--simular", "")])
def test_temporada_rotulo_invalido_sai_com_rc_2(flag, valor, capsys, tmp_path):
    with pytest.raises(SystemExit) as e:
        temporada.main([flag, valor, "--saida", str(tmp_path)])
    assert e.value.code == 2
    err = capsys.readouterr().err
    assert "trimestre inválido" in err and "Traceback" not in err
    assert list(tmp_path.iterdir()) == []


def test_temporada_rotulo_valido_passa_pelo_parser_e_normaliza():
    assert temporada._trimestre_arg(" 3t26 ") == "3T26"


@pytest.mark.parametrize("data", ["2026-13-40", "2026-02-30", "15/10/2026", "x"])
def test_triagem_data_invalida_sai_com_rc_2(data, capsys):
    from triagem import rodar
    with pytest.raises(SystemExit) as e:
        rodar.main(["--data", data, "--sem-registro"])
    assert e.value.code == 2
    err = capsys.readouterr().err
    assert "data inválida" in err and "Traceback" not in err


def test_triagem_data_valida_e_aceita():
    from triagem import rodar
    assert rodar._data_iso("2026-10-15") == "2026-10-15"


def test_textos_das_notas_usam_virgula_decimal():
    assert notas._br(0.1048, 4) == "0,1048" and notas._br(18.24, 1) == "18,2"
    import inspect, re
    fonte = inspect.getsource(notas)
    assert not re.search(r"\{[^{}]*:\.\df\}", fonte)
