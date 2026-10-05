"""Põe ferramentas/ no sys.path para os testes importarem os lotes e os motores."""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
