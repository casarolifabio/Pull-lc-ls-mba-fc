"""
Script para fazer pull de prompts do LangSmith Prompt Hub.

Este script:
1. Conecta ao LangSmith usando credenciais do .env
2. Faz pull dos prompts do Hub
3. Salva localmente em prompts/bug_to_user_story_v1.yml

SIMPLIFICADO: Usa serialização nativa do LangChain para extrair prompts.
"""

import os
import sys
from dotenv import load_dotenv
from langsmith import Client
from utils import save_yaml, check_env_vars, print_section_header

load_dotenv()

PROMPT_IDENTIFIER = "leonanluppi/bug_to_user_story_v1"
OUTPUT_PATH = "prompts/bug_to_user_story_v1.yml"


def pull_prompts_from_langsmith():
    """
    Faz pull do prompt do LangSmith Hub e salva localmente.

    Returns:
        True se sucesso, False caso contrário
    """
    try:
        print(f"Conectando ao LangSmith Hub...")
        client = Client()

        print(f"Fazendo pull do prompt: {PROMPT_IDENTIFIER}")
        prompt = client.pull_prompt(PROMPT_IDENTIFIER)

        system_prompt = prompt.messages[0].prompt.template
        user_prompt = "{bug_report}"

        if len(prompt.messages) > 1:
            user_template = prompt.messages[1].prompt.template
            if user_template and user_template != system_prompt:
                user_prompt = user_template

        prompt_data = {
            "bug_to_user_story_v1": {
                "description": "Prompt para converter relatos de bugs em User Stories",
                "system_prompt": system_prompt,
                "user_prompt": user_prompt,
                "version": "v1",
                "created_at": "2025-01-15",
                "tags": ["bug-analysis", "user-story", "product-management"],
            }
        }

        print(f"Salvando prompt em: {OUTPUT_PATH}")
        success = save_yaml(prompt_data, OUTPUT_PATH)

        if success:
            print(f"✓ Prompt salvo com sucesso em {OUTPUT_PATH}")
            return True

        return False

    except Exception as e:
        print(f"❌ Erro ao fazer pull do LangSmith Hub: {e}")
        return False


def main():
    """Função principal"""
    print_section_header("PULL DE PROMPTS DO LANGSMITH HUB")

    required_vars = ["LANGSMITH_API_KEY", "USERNAME_LANGSMITH_HUB"]
    if not check_env_vars(required_vars):
        return 1

    success = pull_prompts_from_langsmith()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
