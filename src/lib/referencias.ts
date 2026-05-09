export type FonteId =
  | "pequeno-livro"
  | "manual-tecnico"
  | "caderneta-crianca"
  | "caderneta-gestante";

export type Fonte = {
  id: FonteId;
  titulo: string;
  autoria: string;
  ano: string;
  descricao: string;
  tipo: "Livro" | "Manual oficial" | "Caderneta oficial";
  icone: string;
};

export const fontes: Record<FonteId, Fonte> = {
  "pequeno-livro": {
    id: "pequeno-livro",
    titulo: "O pequeno livro sobre o puerpério",
    autoria: "Maria Barretto",
    ano: "2020",
    descricao:
      "Olhar sensível e humano sobre o puerpério como rito de passagem. Aborda resguardo, vínculo, rede de apoio, papel do parceiro e a dimensão emocional/espiritual da maternidade.",
    tipo: "Livro",
    icone: "📖"
  },
  "manual-tecnico": {
    id: "manual-tecnico",
    titulo: "Manual Técnico do Pré-Natal e Puerpério",
    autoria: "Secretaria de Estado da Saúde de São Paulo (SES-SP)",
    ano: "2010",
    descricao:
      "Manual técnico oficial para profissionais de saúde do SUS, com diretrizes sobre rotinas de pré-natal, queixas frequentes, intercorrências, aleitamento e atenção ao puerpério.",
    tipo: "Manual oficial",
    icone: "🏥"
  },
  "caderneta-crianca": {
    id: "caderneta-crianca",
    titulo: "Caderneta da Criança – Passaporte da Cidadania",
    autoria: "Ministério da Saúde do Brasil",
    ano: "2024 (7ª edição)",
    descricao:
      "Documento oficial de acompanhamento da criança do nascimento aos 9 anos. Cobre amamentação, alimentação, desenvolvimento, vacinas, sinais de alerta e direitos.",
    tipo: "Caderneta oficial",
    icone: "👶"
  },
  "caderneta-gestante": {
    id: "caderneta-gestante",
    titulo: "Caderneta da Gestante",
    autoria: "Ministério da Saúde do Brasil",
    ano: "Ed. atual",
    descricao:
      "Caderneta oficial usada no pré-natal, com orientações sobre consultas, exames, sinais de alerta na gestação, parto, direitos e cuidados pós-parto.",
    tipo: "Caderneta oficial",
    icone: "🤰"
  }
};

export type Referencia = {
  fonte: FonteId;
  trecho?: string;
};

export function getFonte(id: FonteId) {
  return fontes[id];
}

export function getAllFontes() {
  return Object.values(fontes);
}
