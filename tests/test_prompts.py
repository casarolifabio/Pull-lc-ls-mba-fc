"""
Testes automatizados para validação de prompts.
"""
import pytest
import yaml
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils import validate_prompt_structure

PROMPT_FILE = Path(__file__).parent.parent / "prompts" / "bug_to_user_story_v2.yml"


def load_prompts(file_path: str):
    """Carrega prompts do arquivo YAML."""
    with open(file_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


class TestPrompts:
    @pytest.fixture
    def prompt_v2(self):
        """Carrega o prompt v2 para testes."""
        return load_prompts(str(PROMPT_FILE))

    def test_prompt_has_system_prompt(self, prompt_v2):
        """Verifica se o campo 'system_prompt' existe e não está vazio."""
        prompt_key = list(prompt_v2.keys())[0]
        prompt_data = prompt_v2[prompt_key]

        assert "system_prompt" in prompt_data, "Campo 'system_prompt' ausente"
        system_prompt = prompt_data["system_prompt"]
        assert system_prompt, "Campo 'system_prompt' está vazio"
        assert len(system_prompt.strip()) > 0, "Campo 'system_prompt' contém apenas espaços"

    def test_prompt_has_role_definition(self, prompt_v2):
        """Verifica se o prompt define uma persona (ex: "Você é um Product Manager")."""
        prompt_key = list(prompt_v2.keys())[0]
        prompt_data = prompt_v2[prompt_key]
        system_prompt = prompt_data["system_prompt"].lower()

        role_patterns = [
            "você é um",
            "você é uma",
            "you are a",
            "you are an",
            "atua como",
            "sua função é",
        ]

        has_role = any(pattern in system_prompt for pattern in role_patterns)
        assert has_role, f"Prompt não define persona. Padrões esperados: {role_patterns}"

    def test_prompt_mentions_format(self, prompt_v2):
        """Verifica se o prompt exige formato Markdown ou User Story padrão."""
        prompt_key = list(prompt_v2.keys())[0]
        prompt_data = prompt_v2[prompt_key]
        system_prompt = prompt_data["system_prompt"].lower()

        format_keywords = [
            "markdown",
            "user story",
            "user stories",
            "formato",
            "structure",
            "estrutura",
            "critérios de aceitação",
            "acceptance criteria",
        ]

        mentions_format = any(keyword in system_prompt for keyword in format_keywords)
        assert mentions_format, f"Prompt não menciona formato de saída. Palavras-chave: {format_keywords}"

    def test_prompt_has_few_shot_examples(self, prompt_v2):
        """Verifica se o prompt contém exemplos de entrada/saída (técnica Few-shot)."""
        prompt_key = list(prompt_v2.keys())[0]
        prompt_data = prompt_v2[prompt_key]
        system_prompt = prompt_data["system_prompt"].lower()

        example_patterns = [
            "exemplo",
            "example",
            "input:",
            "output:",
            "bug report:",
            "user story:",
        ]

        has_examples = any(pattern in system_prompt for pattern in example_patterns)
        example_count = system_prompt.count("exemplo") + system_prompt.count("example")

        assert has_examples, "Prompt não contém exemplos few-shot (entrada/saída)"
        assert example_count >= 2, f"Prompt deve ter pelo menos 2 exemplos, encontrados: {example_count}"

    def test_prompt_no_todos(self, prompt_v2):
        """Garante que você não esqueceu nenhum `[TODO]` no texto."""
        prompt_key = list(prompt_v2.keys())[0]
        prompt_data = prompt_v2[prompt_key]

        for field_name, field_value in prompt_data.items():
            if isinstance(field_value, str):
                assert "[TODO]" not in field_value, f"Encontrado [TODO] no campo '{field_name}'"
                assert "[todo]" not in field_value.lower(), f"Encontrado [todo] no campo '{field_name}'"

    def test_minimum_techniques(self, prompt_v2):
        """Verifica (através dos metadados do yaml) se pelo menos 2 técnicas foram listadas."""
        prompt_key = list(prompt_v2.keys())[0]
        prompt_data = prompt_v2[prompt_key]

        assert "techniques_applied" in prompt_data, "Campo 'techniques_applied' ausente nos metadados"

        techniques = prompt_data["techniques_applied"]
        assert isinstance(techniques, list), "Campo 'techniques_applied' deve ser uma lista"
        assert len(techniques) >= 2, f"Mínimo de 2 técnicas requeridas, encontradas: {len(techniques)}"

        non_empty = [t for t in techniques if t and t.strip()]
        assert len(non_empty) >= 2, "Pelo menos 2 técnicas não-vazias são necessárias"

        is_valid, errors = validate_prompt_structure(prompt_data)
        assert is_valid, f"Estrutura do prompt inválida: {errors}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
