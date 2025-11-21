"""
loader.py

Módulo para carregar Base de Dados e Persona conforme arquitetura proposta.

Separação clara:
- data/ = Conhecimento técnico (gestação, parto, pós-parto, vacinação)
- persona/ = Tom de voz e comportamento
- system/ = Regras fixas da IA
"""

import os
import glob
from typing import Optional, Dict, List
import logging

logger = logging.getLogger(__name__)

# Configurações
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
PERSONA_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "persona", "persona.txt")
SYSTEM_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "system", "system_prompt.md")

# Lista de temas permitidos na base de dados
TEMAS_PERMITIDOS = [
    "gestação", "gestacao", "gravidez", "prenatal",
    "parto", "trabalho de parto", "cesárea", "cesarea", "cesariana",
    "pós-parto", "pos-parto", "posparto", "puerpério", "puerperio",
    "amamentação", "amamentacao", "leite materno",
    "vacinação", "vacinacao", "vacina", "vacinas",
    "bebê", "bebe", "recém-nascido", "recem-nascido",
    "cuidados", "guias", "orientação", "orientacao"
]


def load_all_markdown(data_dir: str) -> str:
    """
    Carrega todo o conteúdo .md/.txt da pasta data e concatena.
    Apenas conteúdos sobre temas permitidos são incluídos.
    """
    if not os.path.exists(data_dir):
        logger.warning(f"[LOADER] Pasta data não encontrada: {data_dir}")
        return ""
    
    parts = []
    files_loaded = []
    
    # Busca todos os arquivos .md e .txt na pasta data
    for pattern in ["*.md", "*.txt"]:
        for path in sorted(glob.glob(os.path.join(data_dir, pattern))):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    contents = f.read().strip()
                    if contents:
                        # Verifica se o conteúdo é sobre temas permitidos
                        contents_lower = contents.lower()
                        if any(tema in contents_lower for tema in TEMAS_PERMITIDOS):
                            filename = os.path.basename(path)
                            parts.append(f"### Fonte: {filename}\n{contents}")
                            files_loaded.append(filename)
                            logger.info(f"[LOADER] ✅ Arquivo carregado: {filename}")
                        else:
                            logger.warning(f"[LOADER] ⚠️ Arquivo ignorado (fora do escopo): {os.path.basename(path)}")
            except Exception as e:
                logger.error(f"[LOADER] ❌ Erro ao carregar {path}: {e}")
    
    if not parts:
        logger.warning(f"[LOADER] ⚠️ Nenhum arquivo válido encontrado em {data_dir}")
        return ""
    
    result = "\n\n".join(parts)
    logger.info(f"[LOADER] ✅ Base de dados carregada: {len(files_loaded)} arquivo(s)")
    return result


def load_persona(persona_file: str) -> str:
    """
    Carrega o arquivo de persona (tom de voz e comportamento).
    """
    if not os.path.exists(persona_file):
        logger.warning(f"[LOADER] Arquivo de persona não encontrado: {persona_file}")
        return ""
    
    try:
        with open(persona_file, "r", encoding="utf-8") as f:
            contents = f.read().strip()
            if contents:
                logger.info(f"[LOADER] ✅ Persona carregada: {os.path.basename(persona_file)}")
                return contents
            else:
                logger.warning(f"[LOADER] ⚠️ Arquivo de persona vazio: {persona_file}")
                return ""
    except Exception as e:
        logger.error(f"[LOADER] ❌ Erro ao carregar persona: {e}")
        return ""


def load_system(system_file: str) -> str:
    """
    Carrega o arquivo de system prompt (regras fixas da IA).
    """
    if not os.path.exists(system_file):
        logger.warning(f"[LOADER] Arquivo de system prompt não encontrado: {system_file}")
        return ""
    
    try:
        with open(system_file, "r", encoding="utf-8") as f:
            contents = f.read().strip()
            if contents:
                logger.info(f"[LOADER] ✅ System prompt carregado: {os.path.basename(system_file)}")
                return contents
            else:
                logger.warning(f"[LOADER] ⚠️ Arquivo de system prompt vazio: {system_file}")
                return ""
    except Exception as e:
        logger.error(f"[LOADER] ❌ Erro ao carregar system prompt: {e}")
        return ""


def build_system_prompt(system_text: str, persona_text: str, data_text: str, max_data_length: int = 4500) -> str:
    """
    Monta o system prompt combinando:
    - Regras fixas (system_text)
    - Tom de voz (persona_text)
    - Base de dados (data_text - truncada se necessário)
    
    Args:
        system_text: Texto do system prompt
        persona_text: Texto da persona
        data_text: Texto da base de dados
        max_data_length: Tamanho máximo da base de dados no prompt
    
    Returns:
        System prompt completo
    """
    prompt_parts = []
    
    # 1. System prompt (regras fixas)
    if system_text:
        prompt_parts.append(system_text)
    else:
        prompt_parts.append("Você é uma assistente especializada em gestação, parto, pós-parto, amamentação e vacinação.")
    
    # 2. Restrição sobre usar apenas a Base de Dados
    prompt_parts.append("\nRESTRIÇÃO CRÍTICA: Para qualquer informação factual (gestação, parto, pós-parto, vacinação, guias práticos), utilize APENAS o conteúdo presente na Base de Dados fornecida. Não invente fatos fora do escopo.")
    
    # 3. Persona (tom de voz)
    if persona_text:
        prompt_parts.append(f"\nPERSONA (tom de voz e comportamento):\n{persona_text}")
    
    # 4. Base de Dados (truncada se necessário)
    if data_text:
        # Trunca se muito grande (em produção, use embeddings + retrieval)
        data_snippet = data_text[:max_data_length] if len(data_text) > max_data_length else data_text
        prompt_parts.append(f"\nBASE_DE_DADOS (conteúdo autorizado):\n{data_snippet}")
        
        if len(data_text) > len(data_snippet):
            prompt_parts.append(f"\n[Nota: Base de dados truncada para {max_data_length} caracteres. Conteúdo completo disponível localmente.]")
    
    # 5. Regras adicionais sobre escopo
    prompt_parts.append("""
REGRAS IMPORTANTES SOBRE O CONHECIMENTO BASE:
- Use APENAS o conhecimento base quando a pergunta for especificamente sobre gestação, vacinação, pós-parto ou puerpério
- Para declarações de sentimentos simples (ex: "estou feliz", "estou triste"), responda de forma empática e conversacional SEM usar o conhecimento base
- Para perguntas sobre você (reciprocidade), responda de forma detalhada e empática SEM usar o conhecimento base
- NUNCA mencione informações do conhecimento base quando não forem relevantes à pergunta do usuário
""")
    
    return "\n".join(prompt_parts)


def load_all() -> Dict[str, str]:
    """
    Carrega todos os componentes necessários.
    
    Returns:
        Dict com:
        - 'data': Conteúdo da base de dados
        - 'persona': Conteúdo da persona
        - 'system': Conteúdo do system prompt
        - 'system_prompt': System prompt completo combinado
    """
    logger.info("[LOADER] Iniciando carregamento de Base de Dados, Persona e System Prompt...")
    
    data_text = load_all_markdown(DATA_DIR)
    persona_text = load_persona(PERSONA_FILE)
    system_text = load_system(SYSTEM_FILE)
    
    # Constrói o system prompt completo
    system_prompt = build_system_prompt(system_text, persona_text, data_text)
    
    logger.info("[LOADER] ✅ Carregamento completo finalizado")
    
    return {
        "data": data_text,
        "persona": persona_text,
        "system": system_text,
        "system_prompt": system_prompt
    }


# Teste rápido
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    result = load_all()
    print(f"\n{'='*60}")
    print(f"Base de dados: {len(result['data'])} caracteres")
    print(f"Persona: {len(result['persona'])} caracteres")
    print(f"System: {len(result['system'])} caracteres")
    print(f"System Prompt completo: {len(result['system_prompt'])} caracteres")
    print(f"{'='*60}")

