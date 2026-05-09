import type { Referencia } from "./referencias";

export type Topico = {
  slug: string;
  titulo: string;
  icone: string;
  badge?: string;
  badgeColor?: "rose" | "green";
  resumo: string;
  intro: string;
  secoes: { titulo: string; itens: string[] }[];
  dicaSophia?: string;
  voltarPara?: { label: string; href: string };
  relacionados?: { slug: string; label: string; icone: string }[];
  referencias?: Referencia[];
};

export const topicos: Record<string, Topico> = {
  "amamentacao": {
    slug: "amamentacao",
    titulo: "Amamentação sem culpa",
    icone: "🍼",
    badge: "Popular",
    badgeColor: "rose",
    resumo: "Pega correta, livre demanda e dicas para fissuras.",
    intro:
      "Amamentar é aprendido — pelo bebê e por você. O leite materno é o alimento mais completo e a recomendação oficial é aleitamento materno exclusivo até os 6 meses, e mantido até os 2 anos ou mais (Ministério da Saúde).",
    secoes: [
      {
        titulo: "Pega correta",
        itens: [
          "A boca do bebê deve abocanhar boa parte da aréola, não só o mamilo.",
          "O queixinho dele encosta no peito e o lábio inferior fica virado para fora.",
          "O nariz fica livre e a aréola aparece mais na parte de cima do que na de baixo da boca.",
          "Você ouve o bebê deglutindo (engolindo) com calma, sem barulhinho de estalo."
        ]
      },
      {
        titulo: "Livre demanda",
        itens: [
          "Ofereça o peito sempre que o bebê pedir, sem cronômetro.",
          "Recém-nascidos mamam de 8 a 12 vezes em 24 horas — é normal.",
          "Cada mamada pode durar entre 10 e 40 minutos. Respeite o ritmo dele.",
          "Quanto mais o bebê suga, mais leite seu corpo produz."
        ]
      },
      {
        titulo: "Fissuras (rachaduras)",
        itens: [
          "Quase sempre indicam pega errada ou posição inadequada — corrija antes.",
          "Passe seu próprio leite no mamilo no fim da mamada e deixe secar ao ar.",
          "Evite sabonetes, cremes e pomadas no mamilo; banho diário e sutiã limpo bastam.",
          "Se a dor persistir, procure consultora em amamentação ou seu obstetra."
        ]
      },
      {
        titulo: "Mamas ingurgitadas",
        itens: [
          "Acontecem habitualmente entre o 3º e o 5º dia após o parto.",
          "Mamas ficam doloridas, edemaciadas, às vezes brilhantes ou com febre baixa.",
          "Mamadas mais frequentes e ordenha manual antes da mamada (para amaciar a aréola) são as estratégias mais lembradas pelo Manual Técnico do SUS — peça à equipe ou a uma consultora em amamentação que te demonstre a técnica.",
          "Mama com região quente, vermelha e febre alta exige avaliação da equipe de saúde — não tente tratar sozinha."
        ]
      },
      {
        titulo: "Pontos que costumam ser lembrados pelo Ministério da Saúde",
        itens: [
          "A recomendação oficial é aleitamento materno exclusivo até os 6 meses, sem oferta de água, chá ou outros leites nesse período (Ministério da Saúde).",
          "Mamadeira, chupeta e protetores de silicone podem interferir na pega — converse com a equipe sobre o que cabe pra sua realidade.",
          "Dietas restritivas para emagrecer durante a amamentação não são recomendadas — qualquer mudança alimentar deve ser conversada com nutricionista ou médico."
        ]
      }
    ],
    dicaSophia:
      "Você não precisa amamentar de forma exclusiva pra ser uma boa mãe. Faça o que for possível, com leveza. 💗",
    voltarPara: { label: "Cuidados com o Bebê", href: "/cuidados-bebe" },
    relacionados: [
      { slug: "sono-do-bebe", label: "Sono do bebê", icone: "😴" },
      { slug: "colicas", label: "Cólicas", icone: "👶" },
      { slug: "alimentacao-pos-parto", label: "Sua alimentação", icone: "🍽️" }
    ],
    referencias: [
      { fonte: "caderneta-crianca", trecho: "Amamentando o Bebê — importância, posição, pega, tempo de mamada e dificuldades." },
      { fonte: "manual-tecnico", trecho: "Atenção ao puerpério — dificuldades com o aleitamento (pega, fissuras, ingurgitamento, mastite, ordenha manual)." },
      { fonte: "pequeno-livro", trecho: "Amamentação como criação de vínculo, lado emocional do peito e o ritmo de cada bebê." }
    ]
  },

  "sono-do-bebe": {
    slug: "sono-do-bebe",
    titulo: "Sono do bebê",
    icone: "😴",
    badge: "Novo",
    badgeColor: "rose",
    resumo: "Ritmos, sonecas e o famoso 'sono leve' nas primeiras semanas.",
    intro:
      "O sono do recém-nascido é fragmentado e isso é fisiológico. Entender o ritmo dele ajuda a respeitar o seu também.",
    secoes: [
      {
        titulo: "Como funciona",
        itens: [
          "Recém-nascidos dormem entre 14 e 17 horas por dia, em vários ciclos curtos.",
          "Ciclos de sono leve são comuns — eles se mexem, fazem ruídos, mas seguem dormindo.",
          "Antes dos 4 meses, o sono ainda está se organizando. Não compare com outros bebês."
        ]
      },
      {
        titulo: "Sono seguro (ABC)",
        itens: [
          "A — Alone (sozinho no berço, sem travesseiros, mantas grossas ou bichos).",
          "B — On the Back (de barriga pra cima, sempre — reduz risco de morte súbita).",
          "C — Crib (berço firme, com lençol bem esticado)."
        ]
      },
      {
        titulo: "Como você pode descansar",
        itens: [
          "Durma quando o bebê dorme, mesmo de dia.",
          "Aceite ajuda: alguém pode segurar o bebê pra você cochilar 30 minutos.",
          "Não se cobre por 'fazer mais coisas'. Repouso é parte da recuperação."
        ]
      }
    ],
    dicaSophia:
      "Cansaço extremo merece ser ouvido. Se está pesado demais, vamos conversar? Estou aqui. 🌿",
    voltarPara: { label: "Cuidados com o Bebê", href: "/cuidados-bebe" },
    relacionados: [
      { slug: "amamentacao", label: "Amamentação", icone: "🍼" },
      { slug: "colicas", label: "Cólicas", icone: "👶" },
      { slug: "sono-fragmentado", label: "Seu sono no puerpério", icone: "🌙" }
    ],
    referencias: [
      { fonte: "caderneta-crianca", trecho: "Atenção e cuidados especiais — posição segura no sono (de barriga para cima)." }
    ]
  },

  "banho-do-bebe": {
    slug: "banho-do-bebe",
    titulo: "Banho do recém-nascido",
    icone: "🛁",
    badge: "Prático",
    badgeColor: "rose",
    resumo: "Passo a passo seguro para o primeiro banho em casa.",
    intro:
      "Os primeiros banhos podem dar friozinho na barriga. Com calma e organização, vira um momento gostoso.",
    secoes: [
      {
        titulo: "Antes do banho",
        itens: [
          "Separe tudo perto: roupa, fralda, toalha, sabonete, álcool 70%, soro.",
          "Temperatura da água entre 36°C e 37°C (use o cotovelo se não tiver termômetro).",
          "Ambiente fechado, sem corrente de ar, com a temperatura agradável."
        ]
      },
      {
        titulo: "Durante o banho",
        itens: [
          "Apoie a cabecinha e o pescoço com firmeza, mas sem apertar.",
          "Comece pelo rosto, depois cabeça, corpo e por último a região da fralda.",
          "O banho não precisa demorar — 5 a 10 minutos já é o bastante."
        ]
      },
      {
        titulo: "Depois do banho",
        itens: [
          "Seque com toques suaves, sem esfregar, dando atenção às dobrinhas.",
          "A higiene do coto umbilical até a queda costuma ser orientada pela equipe da maternidade — siga exatamente o passo a passo que te ensinaram.",
          "Vista o bebê em camadas (uma a mais do que você está usando)."
        ]
      }
    ],
    dicaSophia: "Bebê chorando no banho é comum nas primeiras semanas. Fale baixinho, mantenha contato com sua pele e respire fundo. 💗",
    voltarPara: { label: "Cuidados com o Bebê", href: "/cuidados-bebe" },
    relacionados: [
      { slug: "coto-umbilical", label: "Coto umbilical", icone: "💧" },
      { slug: "amamentacao", label: "Amamentação", icone: "🍼" }
    ],
    referencias: [
      { fonte: "caderneta-crianca", trecho: "Os primeiros dias de vida — orientações de higiene do recém-nascido." }
    ]
  },

  "coto-umbilical": {
    slug: "coto-umbilical",
    titulo: "Coto umbilical",
    icone: "💧",
    badge: "Cuidado",
    badgeColor: "rose",
    resumo: "Limpeza, sinais de alerta e cuidados diários.",
    intro:
      "O coto umbilical seca e cai naturalmente entre 7 e 21 dias. Veja a seguir o que costuma ser orientado pela equipe de saúde na maternidade — peça que te demonstrem antes da alta e siga sempre o que a sua equipe orientar.",
    secoes: [
      {
        titulo: "Como costuma ser orientado",
        itens: [
          "A higiene da base do coto a cada troca de fralda é o cuidado mais lembrado por pediatras e cadernetas oficiais (frequentemente com álcool 70%, conforme a orientação que você recebeu).",
          "Não cobrir com curativo nem 'barriguilha' — quanto mais arejado, melhor.",
          "Manter a fralda dobrada abaixo do coto."
        ]
      },
      {
        titulo: "O que é normal",
        itens: [
          "Pequena secreção amarelada ou um cheirinho ao secar.",
          "Pequenas manchas de sangue no momento da queda.",
          "O coto escurece e enruga antes de cair."
        ]
      },
      {
        titulo: "Sinais de alerta",
        itens: [
          "Pele em volta vermelha, quente ou inchada.",
          "Pus, mau cheiro forte ou sangramento contínuo.",
          "Bebê com febre ou muito molinho — procure o pediatra."
        ]
      }
    ],
    dicaSophia: "Na dúvida, foto e mensagem para o pediatra. Não fique sozinha com a preocupação. 🌿",
    voltarPara: { label: "Cuidados com o Bebê", href: "/cuidados-bebe" },
    relacionados: [
      { slug: "banho-do-bebe", label: "Banho do bebê", icone: "🛁" },
      { slug: "sinais-alerta", label: "Sinais de alerta", icone: "🌡️" }
    ],
    referencias: [
      { fonte: "caderneta-crianca", trecho: "Consulta da 1ª Semana — observação do coto umbilical e sinais de alerta." }
    ]
  },

  "colicas": {
    slug: "colicas",
    titulo: "Cólicas do bebê",
    icone: "👶",
    badge: "Frequente",
    badgeColor: "rose",
    resumo: "Massagens, posições e quando se preocupar.",
    intro:
      "As cólicas costumam aparecer entre a 2ª e a 6ª semana. É um dos momentos mais difíceis do puerpério, mas passa.",
    secoes: [
      {
        titulo: "Estratégias frequentemente lembradas por famílias e pediatras",
        itens: [
          "Posição de bruços no antebraço da pessoa que está com o bebê (posição da 'cobrinha').",
          "Conforto térmico suave na barriga (jamais quente, sempre com paninho entre) — algumas famílias relatam alívio.",
          "Massagem em movimentos circulares, no sentido horário, ao redor do umbigo.",
          "Antes de tentar qualquer manobra, vale conversar com o pediatra da criança sobre o que se aplica ao seu bebê."
        ]
      },
      {
        titulo: "Durante a crise",
        itens: [
          "Mantenha o bebê próximo, em pele com pele se possível.",
          "Música suave ou ruído branco podem acalmar.",
          "Faça pausas: passe o bebê pra alguém de confiança quando puder."
        ]
      },
      {
        titulo: "Quando procurar o pediatra",
        itens: [
          "Choro inconsolável por mais de 3h sem alívio em vários dias.",
          "Bebê com febre, vomitando ou com sangue nas fezes.",
          "Você sentindo que não está bem para cuidar — peça ajuda."
        ]
      }
    ],
    dicaSophia: "Cólica cansa duas vezes: o bebê e você. Reveze, descanse, respire. Você está fazendo o melhor possível. 💕",
    voltarPara: { label: "Cuidados com o Bebê", href: "/cuidados-bebe" },
    relacionados: [
      { slug: "amamentacao", label: "Amamentação", icone: "🍼" },
      { slug: "sono-do-bebe", label: "Sono do bebê", icone: "😴" }
    ],
    referencias: [
      { fonte: "caderneta-crianca", trecho: "Acompanhamento da criança — cólicas e funcionamento intestinal nos primeiros meses." }
    ]
  },

  "vacinas": {
    slug: "vacinas",
    titulo: "Vacinas do bebê",
    icone: "💉",
    badge: "Essencial",
    badgeColor: "green",
    resumo: "Visão geral do calendário oficial — confirmação é com o pediatra/UBS.",
    intro:
      "As vacinas do bebê são gratuitas pelo SUS e protegem contra doenças graves. O conteúdo abaixo é uma visão geral do Calendário Nacional de Vacinação (Caderneta da Criança, Ministério da Saúde) — quem confirma o que está em dia, o que foi adiado e o que cabe ao seu bebê é o pediatra ou a equipe da UBS.",
    secoes: [
      {
        titulo: "Ao nascer (ainda na maternidade)",
        itens: [
          "BCG (tuberculose) — dose única.",
          "Hepatite B — 1ª dose, nas primeiras 12 a 24 horas de vida."
        ]
      },
      {
        titulo: "Aos 2 meses",
        itens: [
          "Pentavalente (DTP + Hib + Hepatite B).",
          "VIP (poliomielite injetável).",
          "Pneumocócica 10-valente.",
          "Rotavírus humano (VORH).",
          "É comum aparecer febre baixa e dor local após a vacina — qualquer manejo (uso de antitérmico, compressas etc.) deve ser orientado pelo pediatra antes."
        ]
      },
      {
        titulo: "Aos 3 meses",
        itens: [
          "Meningocócica C (1ª dose)."
        ]
      },
      {
        titulo: "Aos 4 e 6 meses",
        itens: [
          "Reforços de Pentavalente, VIP, Pneumocócica 10 e Rotavírus.",
          "Aos 5 meses: 2ª dose de Meningocócica C."
        ]
      },
      {
        titulo: "Aos 9 meses",
        itens: [
          "Febre Amarela (em áreas de recomendação)."
        ]
      },
      {
        titulo: "Aos 12 meses",
        itens: [
          "Tríplice viral (sarampo, caxumba, rubéola).",
          "Pneumocócica 10 (reforço).",
          "Meningocócica C (reforço)."
        ]
      },
      {
        titulo: "Aos 15 meses",
        itens: [
          "DTP (1º reforço), VOP (poliomielite oral), Hepatite A.",
          "Tetraviral (sarampo, caxumba, rubéola e varicela)."
        ]
      }
    ],
    dicaSophia:
      "Anote as datas no celular ou na caderneta. Se atrasar, o pediatra orienta. Sem culpa, ok? 💗",
    voltarPara: { label: "Cuidados com o Bebê", href: "/cuidados-bebe" },
    relacionados: [
      { slug: "sinais-alerta", label: "Sinais de alerta", icone: "🌡️" },
      { slug: "triagem-neonatal", label: "Triagem neonatal", icone: "🧪" },
      { slug: "estimulos-seguros", label: "Estímulos seguros", icone: "🧸" }
    ],
    referencias: [
      { fonte: "caderneta-crianca", trecho: "Calendário Nacional de Vacinação da Criança — Ministério da Saúde, 2024." }
    ]
  },

  "estimulos-seguros": {
    slug: "estimulos-seguros",
    titulo: "Estímulos seguros",
    icone: "🧸",
    resumo: "Brincadeiras simples por idade, no tempo do bebê.",
    intro:
      "Bebê não precisa de muitos brinquedos — precisa de você. O melhor estímulo é o vínculo. Conversar, cantar, ler e olhar nos olhos do bebê estimula o cérebro e fortalece o apego.",
    secoes: [
      {
        titulo: "0 a 2 meses",
        itens: [
          "O bebê enxerga até cerca de 20 cm — a distância do seu rosto enquanto amamenta.",
          "Aproxime o rosto e converse de forma carinhosa, faça contato visual.",
          "Cante canções de ninar — música transmite tranquilidade.",
          "Coloque o bebê de bruços por curtos períodos (tummy time) para fortalecer o pescoço."
        ]
      },
      {
        titulo: "2 a 4 meses",
        itens: [
          "Ofereça brinquedos coloridos para ele tocar — ainda não busca, só toca e bate.",
          "Leia em voz alta. Cante músicas com repetições — bebês adoram a voz dos pais.",
          "Estabeleça pequenas rotinas de mamada, banho e brincadeira."
        ]
      },
      {
        titulo: "4 a 6 meses",
        itens: [
          "Brinquedos macios, mordedores, chocalhos. Ele já leva à boca.",
          "Use a fala materna ('manhês') alongando vogais, mas com pronúncia correta.",
          "Aponte e nomeie objetos: 'isto é uma bola', 'olha o gatinho'.",
          "Livros de pano e plástico com cores fortes funcionam bem."
        ]
      }
    ],
    dicaSophia: "Você é o brinquedo favorito do seu bebê. Sua voz, seu cheiro, seu colo. Não tem nada melhor. 🌿",
    voltarPara: { label: "Cuidados com o Bebê", href: "/cuidados-bebe" },
    relacionados: [
      { slug: "vacinas", label: "Vacinas", icone: "💉" },
      { slug: "desenvolvimento-bebe", label: "Marcos do desenvolvimento", icone: "🌱" },
      { slug: "sono-do-bebe", label: "Sono do bebê", icone: "😴" }
    ],
    referencias: [
      { fonte: "caderneta-crianca", trecho: "Estimulando o Desenvolvimento com Afeto — orientações por faixa etária." }
    ]
  },

  "sinais-alerta": {
    slug: "sinais-alerta",
    titulo: "Sinais de alerta no bebê",
    icone: "🌡️",
    badge: "Importante",
    badgeColor: "rose",
    resumo: "Quando ir ao pediatra sem hesitar.",
    intro:
      "Confiar na sua intuição é um cuidado também. Esses sinais merecem atenção rápida — se não conseguir levar a criança ao serviço, ligue 192 (SAMU).",
    secoes: [
      {
        titulo: "Procurar atendimento agora (menores de 2 meses)",
        itens: [
          "Criança muito molinha, que se movimenta menos que o normal.",
          "Muito sonolenta, com dificuldade para acordar.",
          "Não consegue mamar.",
          "Febre (≥ 37,5°C) ou temperatura baixa (≤ 35,5°C).",
          "Dificuldade ou respiração muito rápida.",
          "Convulsão (tremores) ou perda de consciência.",
          "Pus saindo do ouvido, manchas avermelhadas/arroxeadas, urina escura ou fezes com sangue."
        ]
      },
      {
        titulo: "Procurar atendimento agora (maiores de 2 meses)",
        itens: [
          "Dificuldade ou respiração rápida.",
          "Não consegue mamar ou tomar líquidos.",
          "Vomita tudo o que come e bebe.",
          "Pele com pouca elasticidade (sinal de desidratação).",
          "Convulsão ou perda da consciência.",
          "Manchas avermelhadas ou arroxeadas na pele."
        ]
      },
      {
        titulo: "Sinais de desidratação",
        itens: [
          "Olhos fundos, choro sem lágrimas, pouca saliva, urina escassa.",
          "Sede intensa, pele com pouca elasticidade.",
          "Em caso de diarreia, busque atendimento — o soro de reidratação oral é distribuído gratuitamente nas UBS e o uso correto é orientado pela equipe de saúde."
        ]
      }
    ],
    dicaSophia: "Confie na sua leitura de mãe. Se algo está estranho, ligue. Médico foi feito pra isso. 💗",
    voltarPara: { label: "Cuidados com o Bebê", href: "/cuidados-bebe" },
    relacionados: [
      { slug: "vacinas", label: "Vacinas", icone: "💉" },
      { slug: "colicas", label: "Cólicas", icone: "👶" }
    ],
    referencias: [
      { fonte: "caderneta-crianca", trecho: "Sinais de Perigo — quando procurar o serviço de saúde imediatamente." }
    ]
  },

  "primeiros-40-dias": {
    slug: "primeiros-40-dias",
    titulo: "Os primeiros 40 dias",
    icone: "🤱",
    badge: "Essencial",
    badgeColor: "rose",
    resumo: "O que esperar do resguardo, repouso e cuidados básicos.",
    intro:
      "O resguardo é o período de adaptação do seu corpo, do bebê e da família. É um tempo sagrado de descanso e recuperação. Tradições antigas já tratavam essa fase com reverência — a medicina moderna também reconhece sua importância.",
    secoes: [
      {
        titulo: "Repouso é remédio",
        itens: [
          "Limite visitas: ninguém precisa ver o bebê na primeira semana.",
          "Cama, sofá e colo. Tarefas pesadas podem esperar.",
          "Boa hidratação é frequentemente lembrada pela equipe do pré-natal/puerpério.",
          "Após cesárea é comum a equipe orientar evitar escadas e carregar peso na primeira semana — siga as orientações que você recebeu na alta."
        ]
      },
      {
        titulo: "Sangramento (lóquios)",
        itens: [
          "Os lóquios são normais e duram até 6 semanas, mudando de cor (vermelho, rosado, amarelado).",
          "É comum a equipe de saúde orientar uso de absorventes externos pós-parto, sem absorvente interno.",
          "Retorno brusco de sangramento intenso após melhorar é sinal para procurar o serviço de saúde."
        ]
      },
      {
        titulo: "Pontos e cesárea",
        itens: [
          "A higiene local da episiotomia é tema da consulta de revisão de puerpério — peça à equipe que te oriente sobre como cuidar.",
          "Na cesárea, é comum a orientação de evitar esforços e curvar-se; uso de cinta, quando indicado, é orientação médica individual.",
          "Vermelhidão, pus, dor que piora ou febre são sinais para procurar a equipe imediatamente."
        ]
      },
      {
        titulo: "Consultas pós-parto",
        itens: [
          "Primeira consulta da puérpera e do RN: idealmente entre o 3º e o 5º dia de vida.",
          "Consulta puerperal entre 30 e 42 dias após o parto, com avaliação clínica e ginecológica.",
          "É no retorno do puerpério que a equipe avalia a atualização vacinal — converse com a sua UBS."
        ]
      }
    ],
    dicaSophia: "Você acabou de fazer um milagre. Seu corpo merece ser tratado com reverência. Aceite ajuda, sem pesar. 💗",
    voltarPara: { label: "Pós-Parto", href: "/pos-parto" },
    relacionados: [
      { slug: "amamentacao", label: "Amamentação", icone: "🍼" },
      { slug: "rede-de-apoio", label: "Rede de apoio", icone: "🫂" },
      { slug: "recuperacao-corpo", label: "Recuperação do corpo", icone: "🩸" }
    ],
    referencias: [
      { fonte: "manual-tecnico", trecho: "Atenção ao puerpério — primeira semana e consulta entre 30 e 42 dias após o parto." },
      { fonte: "pequeno-livro", trecho: "O resguardo — repouso físico, emocional e espiritual após o parto." }
    ]
  },

  "autocuidado": {
    slug: "autocuidado",
    titulo: "Autocuidado possível",
    icone: "🌿",
    badge: "Gentil",
    badgeColor: "green",
    resumo: "Pequenos gestos que cabem na rotina e fazem diferença.",
    intro:
      "Autocuidado no puerpério não é spa. É lavar o rosto, comer com calma, beber água. Coisas mínimas que reabastecem.",
    secoes: [
      {
        titulo: "Cinco minutos pra você",
        itens: [
          "Tomar um banho quente prestando atenção na água.",
          "Beber um chá morninho enquanto o bebê dorme.",
          "Trocar de roupa, mesmo que pra outra de pijama limpa."
        ]
      },
      {
        titulo: "Pequenos prazeres",
        itens: [
          "Música que você gosta, em volume baixo.",
          "Chamada rápida com uma amiga querida.",
          "Olhar pela janela, respirar fundo, alongar o pescoço."
        ]
      }
    ],
    dicaSophia: "Pequeno também conta. Você não precisa fazer 'muito' pra cuidar de si. 💕",
    voltarPara: { label: "Saúde Emocional", href: "/saude-emocional" },
    relacionados: [
      { slug: "respiracao", label: "Respiração de 5 min", icone: "🌬️" },
      { slug: "autocompaixao", label: "Autocompaixão", icone: "💗" }
    ],
    referencias: [
      { fonte: "pequeno-livro", trecho: "Pequenos gestos de cuidado consigo durante o resguardo." }
    ]
  },

  "alimentacao-pos-parto": {
    slug: "alimentacao-pos-parto",
    titulo: "Alimentação no puerpério",
    icone: "🍽️",
    badge: "Energia",
    badgeColor: "green",
    resumo: "Comidas que ajudam na recuperação e na produção de leite.",
    intro:
      "No puerpério, comer é cuidado. Refeições simples, em mais vezes ao dia, ajudam o corpo a se recuperar.",
    secoes: [
      {
        titulo: "Para a recuperação",
        itens: [
          "Proteínas: ovos, frango, peixe, feijão, lentilha.",
          "Ferro: carnes vermelhas, folhas verde-escuras, beterraba.",
          "A suplementação de ferro no pós-parto é uma das condutas previstas em protocolos do SUS — quem avalia se você precisa, em que dose e por quanto tempo é o seu médico ou enfermeiro do pré-natal/puerpério.",
          "Gorduras boas: abacate, castanhas, azeite extra-virgem."
        ]
      },
      {
        titulo: "Para amamentar",
        itens: [
          "Hidratação ampla é frequentemente lembrada por nutricionistas no puerpério — tenha sempre uma garrafinha por perto.",
          "Alimentos como aveia, gergelim e linhaça aparecem muito na sabedoria popular sobre lactação — não há comprovação científica forte, mas são parte de uma alimentação variada.",
          "Não existe alimento proibido universal na amamentação — qualquer suspeita de reação no bebê deve ser conversada com pediatra/nutricionista.",
          "Nunca use medicamentos, suplementos ou fitoterápicos por conta própria — quem avalia o que é seguro durante a amamentação é o médico ou farmacêutico."
        ]
      },
      {
        titulo: "Praticidade",
        itens: [
          "Aceite ajuda pra preparar marmitas ou peça delivery saudável.",
          "Tenha snacks fáceis (frutas, iogurte, castanhas) ao lado do sofá.",
          "Coma quando puder, sem pular refeições."
        ]
      }
    ],
    dicaSophia: "Comer é cuidar. Não pule refeições por 'falta de tempo'. Você precisa de combustível. 🌿",
    voltarPara: { label: "Dicas e Conteúdos", href: "/dicas" },
    relacionados: [
      { slug: "amamentacao", label: "Amamentação", icone: "🍼" },
      { slug: "rede-de-apoio", label: "Rede de apoio", icone: "🫂" }
    ],
    referencias: [
      { fonte: "manual-tecnico", trecho: "Atenção ao puerpério — orientações nutricionais e suplementação de ferro." }
    ]
  },

  "rede-de-apoio": {
    slug: "rede-de-apoio",
    titulo: "Rede de apoio",
    icone: "🫂",
    badge: "Apoio",
    badgeColor: "green",
    resumo: "Como pedir ajuda sem culpa e organizar o que delegar.",
    intro:
      "Pedir ajuda não é fraqueza, é sabedoria. Mães cercadas de apoio se recuperam melhor — fato. Como diz Maria Barretto, no 'Pequeno livro sobre o puerpério': 'é preciso uma aldeia para cuidar de uma mulher que acaba de parir'.",
    secoes: [
      {
        titulo: "Quem pode ajudar",
        itens: [
          "Parceiro(a): trocas, banho, levar o bebê pra você descansar — e principalmente cuidar de você.",
          "Família próxima: refeições, lavar roupa, companhia silenciosa.",
          "Amigas: visitas curtas que tragam algo, não esperem ser servidas.",
          "Doulas pós-parto: profissionais especializadas em apoio no puerpério."
        ]
      },
      {
        titulo: "Como pedir",
        itens: [
          "Seja específica: 'pode trazer um almoço quarta?' funciona melhor que 'me ajuda'.",
          "Tenha uma lista de tarefas visível pra quem chegar.",
          "Não diga 'não precisa' por educação. Aceite. Agradeça depois.",
          "Crie um grupo no celular com 10 a 15 pessoas que possam revezar cuidado."
        ]
      },
      {
        titulo: "Quando o apoio falta",
        itens: [
          "Procure grupos de mães online ou presenciais — você não está sozinha.",
          "Doulas pós-parto e enfermeiras particulares podem ser boas opções.",
          "Conheça programas locais (CRAS, ESF) — assistência social pode ajudar.",
          "Converse com a Sophia sobre como você está se sentindo."
        ]
      }
    ],
    dicaSophia: "Você não precisa dar conta de tudo sozinha. Mãe com rede é mãe inteira. 💗",
    voltarPara: { label: "Dicas e Conteúdos", href: "/dicas" },
    relacionados: [
      { slug: "autocompaixao", label: "Autocompaixão", icone: "💗" },
      { slug: "conversa-com-parceiro", label: "Conversa com o parceiro", icone: "🫂" }
    ],
    referencias: [
      { fonte: "pequeno-livro", trecho: "A aldeia: criando círculos de apoio e a importância de pedir ajuda no puerpério." }
    ]
  },

  "sexualidade-pos-parto": {
    slug: "sexualidade-pos-parto",
    titulo: "Sexualidade no pós-parto",
    icone: "💗",
    badge: "Honesto",
    badgeColor: "rose",
    resumo: "Conversa franca sobre desejo, corpo e tempo de cada uma.",
    intro:
      "Não existe data exata pra voltar. O retorno depende de você, do seu corpo e do seu emocional. Cerca de 80% das mulheres retomam a atividade sexual em até 6 semanas — mas seu tempo é único.",
    secoes: [
      {
        titulo: "O que esperar",
        itens: [
          "Ressecamento vaginal por causa hormonal — comum, especialmente amamentando.",
          "Mudanças hormonais podem causar desconforto local; quem avalia o que se aplica ao seu caso é a sua ginecologista.",
          "Libido baixa nos primeiros meses é comum e não significa que algo está errado.",
          "A retomada da atividade sexual costuma ser conversada na consulta de revisão de puerpério (~30 a 42 dias) — mas o tempo de cada mulher é único."
        ]
      },
      {
        titulo: "Conversa com o parceiro",
        itens: [
          "Fale honestamente sobre o que você está sentindo, sem cobrança.",
          "Intimidade não é só sexo — abraço, beijo, conversa também contam.",
          "Dor durante a penetração é um sinal para conversar com a ginecologista — ela faz a avaliação."
        ]
      },
      {
        titulo: "Anticoncepção",
        itens: [
          "Mesmo amamentando exclusivamente e sem menstruar, ovulação pode acontecer.",
          "Existem vários métodos descritos como compatíveis com amamentação — qual é o melhor pra você é decisão tomada com a ginecologista, considerando seu corpo, a forma de amamentar e seus planos."
        ]
      }
    ],
    dicaSophia: "Seu corpo está se reorganizando. Vá no seu ritmo. Conversar com seu parceiro sobre isso já é um avanço. 🌿",
    voltarPara: { label: "Saúde Emocional", href: "/saude-emocional" },
    relacionados: [
      { slug: "conversa-com-parceiro", label: "Conversa com o parceiro", icone: "🫂" },
      { slug: "contracepcao-pos-parto", label: "Contracepção", icone: "💊" },
      { slug: "recuperacao-corpo", label: "Recuperação do corpo", icone: "🩸" }
    ],
    referencias: [
      { fonte: "manual-tecnico", trecho: "Atenção ao puerpério — atividade sexual e contracepção no pós-parto." },
      { fonte: "pequeno-livro", trecho: "Sexualidade no puerpério como parte da recriação do corpo." }
    ]
  },

  "baby-blues": {
    slug: "baby-blues",
    titulo: "Baby blues x depressão pós-parto",
    icone: "🌧️",
    badge: "Cuidado",
    badgeColor: "rose",
    resumo: "Como diferenciar a tristeza passageira de algo que precisa de ajuda.",
    intro:
      "Sentir tristeza, choro fácil e oscilação de humor nas primeiras semanas é comum e tem base hormonal. Mas há um limite — saber reconhecer ajuda. O Manual Técnico do SUS reforça que a equipe de saúde deve estar atenta a sinais de blues puerperal e depressão pós-parto em todas as consultas.",
    secoes: [
      {
        titulo: "Baby blues",
        itens: [
          "Acontece em até 80% das mulheres, geralmente nos primeiros 10-15 dias.",
          "Choro fácil, irritabilidade, ansiedade leve, sensibilidade aumentada.",
          "Some sozinho com apoio, repouso e tempo (até 2 semanas)."
        ]
      },
      {
        titulo: "Depressão pós-parto",
        itens: [
          "Sintomas que duram mais de 2 semanas e atrapalham seu dia a dia.",
          "Tristeza profunda, falta de prazer, culpa intensa, dificuldade de criar vínculo.",
          "Cansaço extremo que não melhora com sono.",
          "Ideação de morte ou de fazer mal a si mesma — atendimento URGENTE."
        ]
      },
      {
        titulo: "O que fazer",
        itens: [
          "Não tente 'aguentar sozinha'. Procure psicóloga, psiquiatra ou seu obstetra.",
          "Compartilhe com alguém de confiança o que está sentindo.",
          "CVV: 188 (24h, gratuito) — você não está sozinha.",
          "Em emergência, vá ao pronto-socorro mais próximo."
        ]
      }
    ],
    dicaSophia: "Pedir ajuda é cuidado, não fraqueza. Estou aqui pra te escutar — e pra te encorajar a procurar quem possa te apoiar mais profundamente. 💗",
    voltarPara: { label: "Saúde Emocional", href: "/saude-emocional" },
    relacionados: [
      { slug: "quando-procurar-ajuda", label: "Quando procurar ajuda", icone: "🤝" },
      { slug: "respiracao", label: "Respiração de 5 min", icone: "🌬️" }
    ],
    referencias: [
      { fonte: "manual-tecnico", trecho: "Aspectos emocionais — blues puerperal, depressão pós-parto e atenção da equipe." },
      { fonte: "pequeno-livro", trecho: "O caos da ausência de resguardo e o impacto emocional não respeitado." }
    ]
  },

  "respiracao": {
    slug: "respiracao",
    titulo: "Respiração de 5 minutos",
    icone: "🌬️",
    badge: "Calma",
    badgeColor: "green",
    resumo: "Exercício guiado para acalmar o sistema nervoso.",
    intro:
      "Quando o peito aperta e tudo parece muito, voltar pra respiração ajuda a sair do automático. Tente agora — você merece esses 5 minutos.",
    secoes: [
      {
        titulo: "Passo a passo",
        itens: [
          "Sente-se confortável, ombros relaxados, mãos no colo.",
          "Inspire pelo nariz contando até 4.",
          "Segure o ar contando até 4.",
          "Expire pela boca contando até 6.",
          "Repita por 5 minutos. Quando a mente vagar, volte à contagem."
        ]
      },
      {
        titulo: "Variações",
        itens: [
          "Mão no peito e mão na barriga: sinta o ar entrar e sair.",
          "Tente fechar os olhos se for seguro (com o bebê dormindo perto).",
          "Coloque uma música suave de fundo, se ajudar."
        ]
      }
    ],
    dicaSophia: "5 minutos respirando devolvem 1 hora de paciência. Vale o investimento. 🌿",
    voltarPara: { label: "Saúde Emocional", href: "/saude-emocional" },
    relacionados: [
      { slug: "autocuidado", label: "Autocuidado possível", icone: "🌿" },
      { slug: "diario-sentimentos", label: "Diário de sentimentos", icone: "📓" }
    ]
  },

  "diario-sentimentos": {
    slug: "diario-sentimentos",
    titulo: "Diário de sentimentos",
    icone: "📓",
    badge: "Reflexão",
    badgeColor: "green",
    resumo: "Escrever liberta. Registre como você está em poucas palavras.",
    intro:
      "Escrever ajuda a organizar o caos interno. Não precisa ser bonito, longo nem coerente. Só precisa ser seu.",
    secoes: [
      {
        titulo: "Como começar",
        itens: [
          "Anote 3 palavras que descrevem o seu dia.",
          "Complete: 'Hoje eu senti...', 'Hoje eu precisei...'.",
          "Não revise. Não corrija. É só pra você."
        ]
      },
      {
        titulo: "Perguntas para se fazer",
        itens: [
          "O que me deu paz hoje, mesmo que pequeno?",
          "Quem eu posso pedir ajuda essa semana?",
          "Que necessidade minha ainda não foi atendida?"
        ]
      }
    ],
    dicaSophia: "Posso te ajudar a escrever também — se quiser, vamos conversar e eu te ajudo a colocar em palavras. 💕",
    voltarPara: { label: "Saúde Emocional", href: "/saude-emocional" },
    relacionados: [
      { slug: "respiracao", label: "Respiração de 5 min", icone: "🌬️" },
      { slug: "autocompaixao", label: "Autocompaixão", icone: "💗" }
    ],
    referencias: [
      { fonte: "pequeno-livro", trecho: "Olhando para dentro — escrita e auto-observação no resguardo." }
    ]
  },

  "quando-procurar-ajuda": {
    slug: "quando-procurar-ajuda",
    titulo: "Quando procurar ajuda",
    icone: "🤝",
    badge: "Importante",
    badgeColor: "rose",
    resumo: "Sinais para conversar com obstetra, doula ou psicóloga.",
    intro:
      "Procurar ajuda não significa que algo está 'errado' com você. Significa que você merece cuidado.",
    secoes: [
      {
        titulo: "Sinais físicos",
        itens: [
          "Sangramento que aumenta após ter melhorado.",
          "Dor intensa que não cede com analgésico.",
          "Febre acima de 38°C ou pontos com pus/vermelhidão.",
          "Mama com região quente, vermelha e dolorida (suspeita de mastite)."
        ]
      },
      {
        titulo: "Sinais emocionais",
        itens: [
          "Tristeza profunda por mais de 2 semanas.",
          "Pensamentos de fazer mal a si ou ao bebê.",
          "Sensação de não conseguir cuidar de você nem do bebê."
        ]
      },
      {
        titulo: "Onde buscar",
        itens: [
          "Seu obstetra, pediatra ou ginecologista.",
          "Unidade Básica de Saúde (UBS) mais próxima — atendimento gratuito pelo SUS.",
          "Psicóloga especializada em maternidade ou perinatal.",
          "CVV: 188 — atendimento gratuito 24h pra emocional.",
          "SAMU: 192 (emergência médica)."
        ]
      }
    ],
    dicaSophia: "Você merece ser bem cuidada. Eu te acompanho nessa decisão. 💗",
    voltarPara: { label: "Saúde Emocional", href: "/saude-emocional" },
    relacionados: [
      { slug: "baby-blues", label: "Baby blues x depressão", icone: "🌧️" },
      { slug: "rede-de-apoio", label: "Rede de apoio", icone: "🫂" }
    ],
    referencias: [
      { fonte: "manual-tecnico", trecho: "Atenção ao puerpério — sinais que exigem avaliação médica imediata." }
    ]
  },

  "autocompaixao": {
    slug: "autocompaixao",
    titulo: "Autocompaixão",
    icone: "💗",
    badge: "Gentil",
    badgeColor: "green",
    resumo: "Você está fazendo o melhor que pode. Respira, mãe.",
    intro:
      "Autocompaixão é tratar você mesma com a mesma ternura que trataria uma amiga muito querida.",
    secoes: [
      {
        titulo: "Lembretes diários",
        itens: [
          "Você não precisa ser perfeita pra ser uma boa mãe.",
          "Errar faz parte. Aprender também.",
          "Seu bebê não precisa de uma mãe ideal — precisa de uma mãe disponível."
        ]
      },
      {
        titulo: "Quando a culpa bater",
        itens: [
          "Pergunte: o que eu diria pra uma amiga nessa situação?",
          "Mude o pensamento de 'eu sou ruim' pra 'eu estou cansada'.",
          "Coloque a mão no coração e respire fundo. Você é amada."
        ]
      }
    ],
    dicaSophia: "Mãe boa é mãe possível. Você está sendo possível, hoje, como dá. Isso é lindo. 💕",
    voltarPara: { label: "Saúde Emocional", href: "/saude-emocional" },
    relacionados: [
      { slug: "diario-sentimentos", label: "Diário de sentimentos", icone: "📓" },
      { slug: "rede-de-apoio", label: "Rede de apoio", icone: "🫂" }
    ],
    referencias: [
      { fonte: "pequeno-livro", trecho: "A maternidade como encontro com a própria sombra e a importância da auto-aceitação." }
    ]
  },

  "conversa-com-parceiro": {
    slug: "conversa-com-parceiro",
    titulo: "Conversa com o parceiro",
    icone: "🫂",
    resumo: "Roteiro para falar de divisão de tarefas e carga mental.",
    intro:
      "A carga mental do puerpério costuma cair sobre a mãe. Conversar abertamente é o primeiro passo pra reequilibrar. Como ressalta Maria Barretto, o papel principal do parceiro é cuidar da mãe — e não apenas dividir as tarefas com o bebê.",
    secoes: [
      {
        titulo: "Como abrir o assunto",
        itens: [
          "Escolha um momento calmo, longe do bebê (mesmo que sejam 10 min).",
          "Comece com 'eu sinto...' em vez de 'você não...'.",
          "Diga uma necessidade clara: 'preciso dormir 4h seguidas pelo menos 1 vez na semana'."
        ]
      },
      {
        titulo: "O que dividir",
        itens: [
          "Tarefas físicas: trocar fralda, dar banho, colocar pra arrotar.",
          "Tarefas mentais: lembrar consultas, comprar fraldas, agendar pediatra.",
          "Cuidado emocional: ouvir você sem tentar resolver."
        ]
      },
      {
        titulo: "O cuidado com você",
        itens: [
          "Pedir colo, abraço, escuta — sem precisar 'merecer'.",
          "Aceitar massagens, refeições, banhos preparados pelo parceiro.",
          "Lembrar que cuidar da mãe é cuidar do bebê também."
        ]
      }
    ],
    dicaSophia: "Você não precisa fazer tudo sozinha pra ser boa mãe. Pedir partilha é amor próprio. 💗",
    voltarPara: { label: "Saúde Emocional", href: "/saude-emocional" },
    relacionados: [
      { slug: "rede-de-apoio", label: "Rede de apoio", icone: "🫂" },
      { slug: "sexualidade-pos-parto", label: "Sexualidade no pós-parto", icone: "💗" }
    ],
    referencias: [
      { fonte: "pequeno-livro", trecho: "A experiência dos pais — o papel do parceiro como sustentação emocional da mulher puérpera." }
    ]
  },

  "plano-de-parto": {
    slug: "plano-de-parto",
    titulo: "Plano de parto",
    icone: "📋",
    badge: "Importante",
    badgeColor: "rose",
    resumo: "Documento que comunica suas escolhas para a equipe.",
    intro:
      "Plano de parto é uma carta com suas preferências para o nascimento. Não é contrato, mas guia a equipe a respeitar suas escolhas.",
    secoes: [
      {
        titulo: "O que incluir",
        itens: [
          "Seus dados, do bebê e da equipe.",
          "Preferências de parto (normal, posição, alívio da dor).",
          "Acompanhante de sua escolha durante todo o processo (Lei 11.108/2005).",
          "Contato pele a pele logo após o nascimento.",
          "Aleitamento na primeira hora ('hora dourada')."
        ]
      },
      {
        titulo: "Como fazer",
        itens: [
          "Converse com seu obstetra antes — ajustes podem ser necessários.",
          "Imprima 2 vias: uma pra mala, outra pra equipe na admissão.",
          "Use linguagem clara: 'desejo', 'prefiro' — não comandos."
        ]
      }
    ],
    dicaSophia: "Plano de parto é exercício de protagonismo. Mesmo que mude na hora, vale ter pensado. 💗",
    voltarPara: { label: "Parto", href: "/parto" },
    relacionados: [
      { slug: "tipos-de-parto", label: "Tipos de parto", icone: "🏥" },
      { slug: "mala-da-maternidade", label: "Mala da maternidade", icone: "💼" },
      { slug: "direitos-da-gestante", label: "Seus direitos", icone: "⚖️" }
    ],
    referencias: [
      { fonte: "caderneta-gestante", trecho: "Plano de parto e direitos da gestante." }
    ]
  },

  "tipos-de-parto": {
    slug: "tipos-de-parto",
    titulo: "Tipos de parto",
    icone: "🏥",
    resumo: "Normal, cesárea, humanizado: prós e cuidados de cada um.",
    intro:
      "Não existe parto melhor — existe o parto possível e seguro pra você e seu bebê. Conhecer ajuda a decidir junto com a equipe.",
    secoes: [
      {
        titulo: "Parto normal",
        itens: [
          "Recuperação em geral mais rápida e menos dolorosa pós.",
          "Trabalho de parto pode durar de algumas horas a mais de um dia.",
          "Permite alívio de dor: analgesia, banho morno, posições, doula."
        ]
      },
      {
        titulo: "Cesárea",
        itens: [
          "A indicação de cesárea é decisão médica, considerando segurança da mãe e do bebê.",
          "Recuperação costuma ser mais lenta, com repouso e cuidados com a cicatriz orientados pela equipe.",
          "Pele a pele e amamentação na primeira hora também são possíveis em parto cesáreo."
        ]
      },
      {
        titulo: "Parto humanizado",
        itens: [
          "Não é tipo, é abordagem: respeito, autonomia e protagonismo.",
          "Pode ser normal ou cesárea — o que muda é o cuidado.",
          "Pesquise hospitais e equipes que praticam essa filosofia."
        ]
      }
    ],
    dicaSophia: "Informação reduz medo. Mas se você se sentir perdida, conversamos juntas. 💕",
    voltarPara: { label: "Parto", href: "/parto" },
    relacionados: [
      { slug: "plano-de-parto", label: "Plano de parto", icone: "📋" },
      { slug: "direitos-da-gestante", label: "Seus direitos", icone: "⚖️" }
    ],
    referencias: [
      { fonte: "caderneta-gestante", trecho: "Tipos de parto e preparação para o nascimento." },
      { fonte: "manual-tecnico", trecho: "Atenção ao parto e ao puerpério — diretrizes do SUS-SP." }
    ]
  },

  "direitos-da-gestante": {
    slug: "direitos-da-gestante",
    titulo: "Seus direitos no parto",
    icone: "⚖️",
    badge: "Conhecer",
    badgeColor: "rose",
    resumo: "Acompanhante, alojamento conjunto e informação clara.",
    intro:
      "Conhecer seus direitos é poder. Eles valem em hospital público e privado.",
    secoes: [
      {
        titulo: "Direitos garantidos por lei",
        itens: [
          "Acompanhante de sua escolha durante todo o trabalho de parto, parto e pós-parto (Lei 11.108/2005).",
          "Alojamento conjunto: bebê com você 24h, salvo necessidade médica.",
          "Informação clara sobre cada procedimento, com direito de aceitar ou recusar.",
          "Hora dourada: contato pele a pele e amamentação na primeira hora.",
          "Não isolamento do bebê salvo necessidade clínica registrada."
        ]
      },
      {
        titulo: "Em caso de violação",
        itens: [
          "Registre: nomes, horários, falas. Pedindo testemunhas.",
          "Ouvidoria do hospital, conselho regional de medicina, MP.",
          "Procure rede de apoio para denunciar — você não está sozinha."
        ]
      }
    ],
    dicaSophia: "Você tem voz. Você tem direitos. E você merece ser tratada com dignidade. 💗",
    voltarPara: { label: "Parto", href: "/parto" },
    relacionados: [
      { slug: "plano-de-parto", label: "Plano de parto", icone: "📋" },
      { slug: "tipos-de-parto", label: "Tipos de parto", icone: "🏥" }
    ],
    referencias: [
      { fonte: "manual-tecnico", trecho: "Aspectos éticos e legais — autonomia da mulher e direito ao acompanhante." }
    ]
  },

  "mala-da-maternidade": {
    slug: "mala-da-maternidade",
    titulo: "Mala da maternidade",
    icone: "💼",
    badge: "Checklist",
    badgeColor: "green",
    resumo: "Lista do que levar para o parto.",
    intro:
      "Deixe a mala pronta a partir da 36ª semana. Coisa de mais ocupa espaço — coisa de menos vira correria.",
    secoes: [
      {
        titulo: "Para o bebê",
        itens: [
          "5 a 7 bodies, calças/macacões e meias.",
          "Toalha com capuz, fraldas RN (uma muda fechada).",
          "Lenços umedecidos sem álcool, pomada de assadura.",
          "Manta para sair da maternidade."
        ]
      },
      {
        titulo: "Para você",
        itens: [
          "3 camisolas com botões na frente (facilita amamentar).",
          "Calcinhas descartáveis ou velhas, sutiãs de amamentação.",
          "Absorventes pós-parto (noturnos longos), chinelo borracha.",
          "Itens de higiene, hidratante labial, escova e prendedor de cabelo."
        ]
      },
      {
        titulo: "Documentos",
        itens: [
          "RG, CPF, cartão do plano (se houver), carteira da gestante.",
          "Plano de parto impresso (2 vias).",
          "Carregador de celular com fio bem longo!"
        ]
      }
    ],
    dicaSophia: "Não esquece o carregador. E se esquecer, alguém compra. Vai dar certo. 💕",
    voltarPara: { label: "Guias Práticos", href: "/guias-praticos" },
    relacionados: [
      { slug: "plano-de-parto", label: "Plano de parto", icone: "📋" },
      { slug: "tipos-de-parto", label: "Tipos de parto", icone: "🏥" }
    ]
  },

  "respiracao-trabalho-parto": {
    slug: "respiracao-trabalho-parto",
    titulo: "Respiração no trabalho de parto",
    icone: "🌬️",
    resumo: "Técnicas para ajudar nas contrações.",
    intro:
      "Respirar conscientemente ajuda a manejar a dor da contração e oxigena bebê e mãe.",
    secoes: [
      {
        titulo: "Entre contrações",
        itens: [
          "Respiração calma e profunda, abdominal, pelo nariz.",
          "Inspire em 4 tempos, expire em 6 tempos.",
          "Visualize seu corpo se abrindo, soltando."
        ]
      },
      {
        titulo: "Durante a contração",
        itens: [
          "Inspire profundo no início, solte ar pela boca soltando som baixo.",
          "Não prenda a respiração — segue com fluxo lento e contínuo.",
          "Som grave (vogal 'A' ou 'O') ajuda a relaxar a mandíbula e o períneo."
        ]
      }
    ],
    dicaSophia: "Praticar antes ajuda muito. 5 minutos por dia faz diferença na hora. 🌿",
    voltarPara: { label: "Parto", href: "/parto" },
    relacionados: [
      { slug: "plano-de-parto", label: "Plano de parto", icone: "📋" },
      { slug: "respiracao", label: "Respiração de 5 min", icone: "🌬️" }
    ]
  },

  "acompanhante-doula": {
    slug: "acompanhante-doula",
    titulo: "Acompanhante e doula",
    icone: "🤝",
    resumo: "Quem pode estar com você e como se preparar.",
    intro:
      "Você tem direito a uma pessoa de confiança o tempo todo. Doulas são profissionais que oferecem suporte físico e emocional adicional.",
    secoes: [
      {
        titulo: "Acompanhante",
        itens: [
          "Pode ser parceiro, mãe, irmã, amiga — quem você escolher.",
          "Direito garantido por lei em qualquer hospital (Lei 11.108/2005).",
          "Ideal: pessoa que conhece seus desejos e te acalma."
        ]
      },
      {
        titulo: "Doula",
        itens: [
          "Não substitui equipe médica — atua junto.",
          "Oferece massagem, posições, suporte emocional, técnicas de respiração.",
          "Estudos mostram que doula reduz tempo de parto e necessidade de intervenção."
        ]
      }
    ],
    dicaSophia: "Quem te acompanha precisa estar do seu lado emocional. Escolha bem — confie no instinto. 💗",
    voltarPara: { label: "Parto", href: "/parto" },
    relacionados: [
      { slug: "plano-de-parto", label: "Plano de parto", icone: "📋" },
      { slug: "rede-de-apoio", label: "Rede de apoio", icone: "🫂" }
    ]
  },

  "trimestre-1": {
    slug: "trimestre-1",
    titulo: "1º trimestre",
    icone: "🌱",
    resumo: "Náuseas, sono e adaptação. Cuidados iniciais.",
    intro:
      "As primeiras 12 semanas são de adaptação intensa. Cansaço, enjoos, sensibilidade emocional — tudo isso é normal. O Manual Técnico do SUS reforça que ambivalência (querer e não querer estar grávida) é um sentimento esperado neste momento.",
    secoes: [
      {
        titulo: "Cuidados",
        itens: [
          "Pré-natal: marque na primeira ausência menstrual confirmada.",
          "Ácido fólico desde antes da gravidez (peça orientação).",
          "Evite álcool, tabaco e medicamentos sem orientação médica.",
          "Vacinas: dTpa, hepatite B, influenza e covid-19 conforme calendário."
        ]
      },
      {
        titulo: "Sintomas comuns",
        itens: [
          "Náuseas e vômitos — tente comer biscoito antes de levantar.",
          "Cansaço extremo — escute seu corpo, descanse.",
          "Mudança de humor, irritabilidade — fale sobre o que sente.",
          "Cólicas leves e sialorreia (salivação excessiva) podem aparecer."
        ]
      },
      {
        titulo: "Sinais de alerta",
        itens: [
          "Sangramento vaginal — procure imediatamente o serviço de saúde.",
          "Dor abdominal intensa.",
          "Vômitos persistentes que impedem alimentação (hiperêmese)."
        ]
      }
    ],
    dicaSophia: "É um trimestre forte — emocional e físico. Vai com calma, mãe. 💕",
    voltarPara: { label: "Gestação", href: "/gestacao" },
    relacionados: [
      { slug: "trimestre-2", label: "2º trimestre", icone: "🌷" },
      { slug: "trimestre-3", label: "3º trimestre", icone: "🌸" },
      { slug: "queixas-gestacao", label: "Queixas frequentes", icone: "🤢" },
      { slug: "pre-natal-consultas", label: "Pré-natal", icone: "🩺" }
    ],
    referencias: [
      { fonte: "manual-tecnico", trecho: "Aspectos emocionais por trimestre — primeiro trimestre da gestação." },
      { fonte: "caderneta-gestante", trecho: "Pré-natal e cuidados no início da gravidez." }
    ]
  },

  "trimestre-2": {
    slug: "trimestre-2",
    titulo: "2º trimestre",
    icone: "🌷",
    resumo: "Energia voltando, exames e movimentos do bebê.",
    intro:
      "Considerado o trimestre mais 'tranquilo' — energia volta e barriguinha começa a aparecer. É o momento de introspecção e de adequação às mudanças corporais.",
    secoes: [
      {
        titulo: "Marcos",
        itens: [
          "Ultrassom morfológico (entre 18 e 24 semanas).",
          "Primeiros movimentos do bebê (entre 16 e 22 semanas).",
          "Curva glicêmica para rastreio de diabetes gestacional."
        ]
      },
      {
        titulo: "Cuidados",
        itens: [
          "Atividade física leve (como caminhada e hidroginástica) só após avaliação e liberação médica — quem define frequência e intensidade é a sua equipe.",
          "Aumento de aporte calórico no 2º trimestre é frequentemente lembrado pelo Manual Técnico do SUS — quem orienta a sua dieta é o nutricionista ou seu pré-natal.",
          "Hidratação e protetor solar (manchas escuras no rosto — cloasma — são comuns).",
          "Comece a pensar no plano de parto e enxoval."
        ]
      },
      {
        titulo: "Vacinas no pré-natal",
        itens: [
          "dTpa (difteria, tétano, coqueluche): a partir da 20ª semana.",
          "Influenza: durante todo o ano nos meses de campanha.",
          "Hepatite B: se não vacinada antes."
        ]
      }
    ],
    dicaSophia: "Aproveita esse pico de energia pra coisas que te dão prazer. Você merece. 🌿",
    voltarPara: { label: "Gestação", href: "/gestacao" },
    relacionados: [
      { slug: "trimestre-1", label: "1º trimestre", icone: "🌱" },
      { slug: "trimestre-3", label: "3º trimestre", icone: "🌸" },
      { slug: "vacinas-gestante", label: "Vacinas na gestação", icone: "💉" }
    ],
    referencias: [
      { fonte: "manual-tecnico", trecho: "Rotinas de pré-natal — exames laboratoriais e orientações nutricionais." }
    ]
  },

  "trimestre-3": {
    slug: "trimestre-3",
    titulo: "3º trimestre",
    icone: "🌸",
    resumo: "Preparação para o parto, plano de parto e mala.",
    intro:
      "A reta final. Bebê crescendo rápido, corpo se preparando — você também precisa se preparar emocionalmente. Ansiedade sobre o parto é normal e esperada.",
    secoes: [
      {
        titulo: "Marcos",
        itens: [
          "Ultrassom de 3º trimestre (avalia crescimento e líquido).",
          "Coleta de estreptococo do grupo B entre 35-37 semanas.",
          "Visita ao hospital onde vai parir.",
          "Decisão sobre plano de parto e equipe."
        ]
      },
      {
        titulo: "Cuidados",
        itens: [
          "Hidrate-se, durma de lado (preferência esquerda).",
          "Movimentos do bebê: fique atenta a redução brusca.",
          "Atenção à pressão arterial — pré-eclâmpsia pode aparecer.",
          "Bolsa rota, contrações regulares, sangramento ou dor de cabeça forte = hospital."
        ]
      },
      {
        titulo: "Direção",
        itens: [
          "Não dirija com mais de 36 semanas, queixas frequentes ou edema acentuado.",
          "Use o cinto de 3 pontos passando abaixo do útero, não sobre ele."
        ]
      }
    ],
    dicaSophia: "Pode dar medo. Pode dar pressa. Pode dar emoção. Tudo isso é normal. Estou aqui. 💗",
    voltarPara: { label: "Gestação", href: "/gestacao" },
    relacionados: [
      { slug: "plano-de-parto", label: "Plano de parto", icone: "📋" },
      { slug: "mala-da-maternidade", label: "Mala da maternidade", icone: "💼" },
      { slug: "intercorrencias-gestacao", label: "Sinais de alerta", icone: "⚠️" }
    ],
    referencias: [
      { fonte: "manual-tecnico", trecho: "Procedimentos técnicos e direção de veículo no terceiro trimestre." }
    ]
  },

  "resguardo": {
    slug: "resguardo",
    titulo: "Resguardo (40 dias)",
    icone: "🏠",
    badge: "Essencial",
    badgeColor: "rose",
    resumo: "Repouso, recuperação física e emocional.",
    intro:
      "O resguardo é um tempo sagrado. Tradições antigas o respeitavam — o moderno tem muito a aprender. Como diz Maria Barretto: 'resguardar é olhar atentamente para si, ver de novo, curar e renascer'.",
    secoes: [
      {
        titulo: "Repouso",
        itens: [
          "Evite carregar peso e subir escadas demais.",
          "Sente, deite, durma quando o bebê dormir.",
          "Tarefas domésticas podem ser delegadas — devem!",
          "Permita-se silenciar e ouvir o que vem de dentro."
        ]
      },
      {
        titulo: "Visitas",
        itens: [
          "Comunique com clareza: 1 ou 2 visitas curtas por dia.",
          "Quem visitar pode trazer comida, lavar uma louça.",
          "Diga 'hoje não' sem culpa quando precisar."
        ]
      },
      {
        titulo: "O lado emocional",
        itens: [
          "Memórias da própria infância podem reaparecer — é parte do processo.",
          "Sentir-se vulnerável, sensível, com canais abertos é esperado.",
          "Escrever, conversar, chorar — tudo isso é caminho de cura."
        ]
      }
    ],
    dicaSophia: "Resguardo não é mimo. É medicina ancestral. Aceita. 💗",
    voltarPara: { label: "Pós-Parto", href: "/pos-parto" },
    relacionados: [
      { slug: "primeiros-40-dias", label: "Primeiros 40 dias", icone: "🤱" },
      { slug: "rede-de-apoio", label: "Rede de apoio", icone: "🫂" }
    ],
    referencias: [
      { fonte: "pequeno-livro", trecho: "O resguardo como camada de proteção da mulher após o parto — corpo, emoção e espírito." }
    ]
  },

  "sono-fragmentado": {
    slug: "sono-fragmentado",
    titulo: "Seu sono no puerpério",
    icone: "🌙",
    resumo: "Ritmos do bebê e como você pode descansar.",
    intro:
      "Privação de sono é uma das partes mais difíceis. Não tem mágica, mas tem estratégia.",
    secoes: [
      {
        titulo: "O que ajuda",
        itens: [
          "Durma quando o bebê dormir, mesmo que seja 20 min de cochilo.",
          "Reveze à noite com o parceiro ou familiar (mesmo amamentando).",
          "Evite cafeína depois das 14h."
        ]
      },
      {
        titulo: "Quando o cansaço pesa demais",
        itens: [
          "Peça ajuda real: alguém ficar 4h com o bebê pra você dormir.",
          "Atenção a sinais de exaustão extrema — pode ser sinal de algo mais.",
          "Conversar com a Sophia ou um profissional."
        ]
      }
    ],
    dicaSophia: "Dormir é cuidado. Não é luxo. Cobre isso, mãe. 💗",
    voltarPara: { label: "Pós-Parto", href: "/pos-parto" },
    relacionados: [
      { slug: "sono-do-bebe", label: "Sono do bebê", icone: "😴" },
      { slug: "rede-de-apoio", label: "Rede de apoio", icone: "🫂" }
    ]
  },

  "recuperacao-corpo": {
    slug: "recuperacao-corpo",
    titulo: "Recuperação do corpo",
    icone: "🩸",
    resumo: "Lóquios, pontos, retorno do ciclo.",
    intro:
      "Seu corpo passou por uma transformação enorme. A recuperação tem etapas — e merece paciência. As alterações morfofuncionais da gravidez perduram por até 4 a 6 semanas após o parto.",
    secoes: [
      {
        titulo: "Sangramento (lóquios)",
        itens: [
          "Vermelho intenso nos primeiros 4 a 5 dias (lóquios rubra).",
          "Vai clareando até virar amarelado por volta da 4ª semana (lóquios serosa, depois alba).",
          "Retorno súbito a sangramento intenso = avise médico."
        ]
      },
      {
        titulo: "Pontos e cesárea",
        itens: [
          "Higiene local após cada xixi (água morna).",
          "Cesárea: cuidado com a cicatriz, evite curvar e pegar peso.",
          "Sinais de infecção: vermelhidão, pus, febre."
        ]
      },
      {
        titulo: "Volta do ciclo",
        itens: [
          "Pode demorar enquanto amamenta exclusivamente — ou não.",
          "Mesmo sem menstruar, ovulação acontece. Pense em contracepção.",
          "Converse com seu ginecologista."
        ]
      }
    ],
    dicaSophia: "Seu corpo está fazendo um trabalho gigante. Olha pra ele com carinho. 💕",
    voltarPara: { label: "Pós-Parto", href: "/pos-parto" },
    relacionados: [
      { slug: "primeiros-40-dias", label: "Primeiros 40 dias", icone: "🤱" },
      { slug: "sexualidade-pos-parto", label: "Sexualidade pós-parto", icone: "💗" },
      { slug: "contracepcao-pos-parto", label: "Contracepção", icone: "💊" }
    ],
    referencias: [
      { fonte: "manual-tecnico", trecho: "Atenção ao puerpério — recuperação física, lóquios e cuidados com cicatrizes." }
    ]
  },

  "pre-natal-consultas": {
    slug: "pre-natal-consultas",
    titulo: "Pré-natal: como funciona",
    icone: "🩺",
    badge: "Importante",
    badgeColor: "green",
    resumo: "Consultas, exames e quando começar.",
    intro:
      "O pré-natal é o acompanhamento da gestação por uma equipe de saúde — e é insubstituível. Este conteúdo é educativo, baseado em fontes oficiais; quem te avalia, pede exames e indica condutas é a sua equipe (médico, enfermeiro, nutricionista). O Ministério da Saúde recomenda no mínimo 6 consultas, mas o ideal é atendimento mensal, com frequência maior perto do final.",
    secoes: [
      {
        titulo: "Quando começar",
        itens: [
          "Assim que confirmar a gravidez (idealmente no 1º trimestre).",
          "Você tem direito ao pré-natal gratuito pelo SUS na UBS mais próxima.",
          "Mesmo em hospital privado, mantenha vínculo com a UBS para vacinas e acesso a urgências."
        ]
      },
      {
        titulo: "Frequência das consultas",
        itens: [
          "Até a 28ª semana: mensais.",
          "Da 28ª à 36ª semana: a cada 2 a 3 semanas.",
          "Da 36ª semana até o parto: semanais."
        ]
      },
      {
        titulo: "Exames de rotina",
        itens: [
          "Tipagem sanguínea / fator Rh.",
          "Hemograma (avalia anemia).",
          "Glicemia de jejum e teste oral de tolerância à glicose (rastreia diabetes gestacional).",
          "Sorologias: HIV, sífilis (VDRL), hepatite B, toxoplasmose, rubéola.",
          "Urina tipo I e urocultura.",
          "Ultrassom obstétrico (1º, 2º e 3º trimestre)."
        ]
      },
      {
        titulo: "Em cada consulta",
        itens: [
          "Pressão arterial, peso, edema.",
          "Altura uterina e batimentos cardíacos do bebê (a partir de ~12 semanas).",
          "Apresentação fetal (a partir do 3º trimestre).",
          "Espaço para perguntas, dúvidas e queixas — peça orientação clara."
        ]
      }
    ],
    dicaSophia: "Anote suas dúvidas no celular antes da consulta. Você merece sair com respostas. 💗",
    voltarPara: { label: "Gestação", href: "/gestacao" },
    relacionados: [
      { slug: "queixas-gestacao", label: "Queixas frequentes", icone: "🤢" },
      { slug: "intercorrencias-gestacao", label: "Sinais de alerta", icone: "⚠️" },
      { slug: "vacinas-gestante", label: "Vacinas na gestação", icone: "💉" }
    ],
    referencias: [
      { fonte: "manual-tecnico", trecho: "Rotinas de atenção pré-natal — frequência das consultas, exames e procedimentos técnicos." },
      { fonte: "caderneta-gestante", trecho: "Caderneta da Gestante — registro de consultas e exames do pré-natal." }
    ]
  },

  "queixas-gestacao": {
    slug: "queixas-gestacao",
    titulo: "Queixas frequentes na gestação",
    icone: "🤢",
    resumo: "Náusea, azia, cãibras: o que fazer e quando se preocupar.",
    intro:
      "Várias queixas físicas são esperadas na gestação por causa das mudanças hormonais e mecânicas. Aqui estão as mais comuns e o que ajuda — sempre conversando com sua equipe de saúde.",
    secoes: [
      {
        titulo: "Náuseas e vômitos",
        itens: [
          "Comuns no 1º trimestre. Coma pequenas porções várias vezes ao dia.",
          "Biscoitos secos antes de levantar ajudam.",
          "Evite frituras, gorduras, cheiros fortes.",
          "Vômitos persistentes que impedem alimentação = avise o médico (hiperêmese)."
        ]
      },
      {
        titulo: "Azia (pirose)",
        itens: [
          "Refeições leves, mais vezes ao dia, são frequentemente lembradas por nutricionistas.",
          "Evitar deitar logo após comer e reduzir café, chocolate e frituras são orientações comuns.",
          "Qualquer medicação para azia na gestação precisa ser indicada pela sua equipe — não use por conta própria."
        ]
      },
      {
        titulo: "Dor lombar",
        itens: [
          "Aumento do peso e da curvatura da lombar pioram a dor.",
          "Compressas mornas, alongamento, hidroginástica ajudam.",
          "Use sapato sem salto, evite carregar peso."
        ]
      },
      {
        titulo: "Cãibras",
        itens: [
          "Mais comuns no 2º e 3º trimestre.",
          "Hidratação adequada e alimentação variada são frequentemente lembradas — qualquer suplementação só com indicação da equipe.",
          "Quando a cãibra começar, esticar a perna lentamente costuma trazer alívio."
        ]
      },
      {
        titulo: "Inchaço (edema)",
        itens: [
          "Inchaço de pés e tornozelos no fim do dia é comum.",
          "Eleve as pernas, evite ficar muito tempo em pé ou sentada.",
          "Inchaço súbito de mãos e rosto, dor de cabeça forte = avise médico (pré-eclâmpsia)."
        ]
      },
      {
        titulo: "Constipação",
        itens: [
          "Hidrate-se, coma fibras (frutas, verduras, integrais).",
          "Atividade física leve ajuda muito.",
          "Não tome laxantes sem orientação."
        ]
      }
    ],
    dicaSophia: "Queixa não é frescura. É linguagem do corpo. Anota e conta na consulta. 🌿",
    voltarPara: { label: "Gestação", href: "/gestacao" },
    relacionados: [
      { slug: "pre-natal-consultas", label: "Pré-natal", icone: "🩺" },
      { slug: "intercorrencias-gestacao", label: "Sinais de alerta", icone: "⚠️" }
    ],
    referencias: [
      { fonte: "manual-tecnico", trecho: "Capítulo 8 — Queixas frequentes da gestação e orientações de manejo." }
    ]
  },

  "intercorrencias-gestacao": {
    slug: "intercorrencias-gestacao",
    titulo: "Sinais de alerta na gestação",
    icone: "⚠️",
    badge: "Urgente",
    badgeColor: "rose",
    resumo: "Quando ir direto ao serviço de saúde.",
    intro:
      "Esses sinais merecem atenção rápida. Na dúvida, vá ao pronto-socorro. É melhor checar do que esperar.",
    secoes: [
      {
        titulo: "Procurar atendimento imediato",
        itens: [
          "Sangramento vaginal em qualquer fase.",
          "Perda de líquido pela vagina (bolsa rota).",
          "Dor abdominal intensa ou contrações regulares antes de 37 semanas.",
          "Dor de cabeça forte que não passa, alterações visuais (manchas, pontos, embaçada).",
          "Inchaço súbito de mãos e rosto.",
          "Pressão arterial alta (≥ 140/90 mmHg)."
        ]
      },
      {
        titulo: "Sinais relacionados ao bebê",
        itens: [
          "Diminuição importante ou ausência de movimentos fetais.",
          "Após 28 semanas, equipes de pré-natal costumam orientar a observar a frequência de movimentos do bebê — peça à sua equipe que te explique como acompanhar e o que é esperado no seu caso."
        ]
      },
      {
        titulo: "Outras situações",
        itens: [
          "Febre acima de 38°C, calafrios.",
          "Vômitos persistentes que impedem alimentação.",
          "Ardência ou queimação ao urinar (suspeita de infecção urinária).",
          "Convulsões — emergência absoluta."
        ]
      }
    ],
    dicaSophia: "Confiar na sua intuição é proteção. Vai conferir, mãe. 💗",
    voltarPara: { label: "Gestação", href: "/gestacao" },
    relacionados: [
      { slug: "pre-natal-consultas", label: "Pré-natal", icone: "🩺" },
      { slug: "queixas-gestacao", label: "Queixas frequentes", icone: "🤢" }
    ],
    referencias: [
      { fonte: "manual-tecnico", trecho: "Capítulo 9 — Intercorrências clínicas na gestação (síndromes hemorrágicas, hipertensão, ITU)." }
    ]
  },

  "vacinas-gestante": {
    slug: "vacinas-gestante",
    titulo: "Vacinas na gestação",
    icone: "💉",
    badge: "Proteção",
    badgeColor: "green",
    resumo: "Visão geral do calendário oficial — confirmação é com sua equipe.",
    intro:
      "O Ministério da Saúde mantém um calendário oficial de vacinas para gestantes — todas gratuitas pelo SUS. O conteúdo abaixo é educativo: quem confirma quais vacinas se aplicam à sua gestação, em que momento e em que esquema é a equipe da sua UBS / pré-natal.",
    secoes: [
      {
        titulo: "Vacinas frequentemente lembradas no calendário oficial",
        itens: [
          "dTpa (difteria, tétano e coqueluche acelular).",
          "Influenza (gripe).",
          "Hepatite B (quando aplicável).",
          "Covid-19, conforme calendário atualizado do Ministério da Saúde."
        ]
      },
      {
        titulo: "Situações especiais",
        itens: [
          "Febre amarela e raiva são exemplos de vacinas avaliadas caso a caso, conforme exposição e área de circulação do vírus.",
          "Quem decide se cabem e em que momento é o profissional do seu pré-natal."
        ]
      },
      {
        titulo: "Vacinas com restrições durante a gestação",
        itens: [
          "Vacinas com vírus vivos atenuados (como tríplice viral, varicela e BCG) costumam ser evitadas durante a gestação.",
          "Algumas são feitas no puerpério, conforme orientação da equipe."
        ]
      }
    ],
    dicaSophia:
      "Leve sua caderneta a cada consulta — é a forma mais segura da equipe acompanhar o que falta e o que já foi feito. 💗",
    voltarPara: { label: "Gestação", href: "/gestacao" },
    relacionados: [
      { slug: "pre-natal-consultas", label: "Pré-natal", icone: "🩺" },
      { slug: "vacinas", label: "Vacinas do bebê", icone: "💉" }
    ],
    referencias: [
      { fonte: "caderneta-gestante", trecho: "Calendário de vacinas para gestantes — Ministério da Saúde." },
      { fonte: "manual-tecnico", trecho: "Imunização durante o pré-natal." }
    ]
  },

  "triagem-neonatal": {
    slug: "triagem-neonatal",
    titulo: "Triagem neonatal: os 5 testes",
    icone: "🧪",
    badge: "Importante",
    badgeColor: "green",
    resumo: "Pezinho, orelhinha, olhinho, coraçãozinho e linguinha.",
    intro:
      "Os testes da triagem neonatal são gratuitos e obrigatórios. Eles detectam doenças tratáveis logo nos primeiros dias de vida.",
    secoes: [
      {
        titulo: "Teste do pezinho (triagem biológica)",
        itens: [
          "Idealmente entre o 3º e o 5º dia de vida.",
          "Detecta doenças como hipotireoidismo congênito, fenilcetonúria, anemia falciforme, fibrose cística e outras.",
          "Coletado por punção do calcanhar, sem riscos.",
          "Reteste é solicitado se necessário."
        ]
      },
      {
        titulo: "Teste do olhinho (reflexo vermelho)",
        itens: [
          "Realizado antes da alta da maternidade.",
          "Detecta catarata congênita, glaucoma, retinoblastoma e outros.",
          "Indolor e rápido, com luz especial."
        ]
      },
      {
        titulo: "Teste da orelhinha (triagem auditiva)",
        itens: [
          "Realizado preferencialmente na maternidade, entre 24 e 48h após o nascimento.",
          "Limite máximo: 1º mês de vida.",
          "Indolor — usa fone que emite sons baixinhos.",
          "Detecta deficiência auditiva precoce."
        ]
      },
      {
        titulo: "Teste do coraçãozinho (oximetria de pulso)",
        itens: [
          "Realizado após 24 horas de vida, ainda na maternidade.",
          "Detecta cardiopatias congênitas críticas.",
          "Sensor no pé e na mão direita do bebê."
        ]
      },
      {
        titulo: "Teste da linguinha",
        itens: [
          "Avalia o frênulo lingual (a 'pele' embaixo da língua).",
          "Detecta a anquiloglossia (língua presa) — pode dificultar a amamentação.",
          "Quando alterado, a equipe avalia se há indicação de seguimento especializado — qualquer conduta é definida pelo profissional habilitado."
        ]
      }
    ],
    dicaSophia: "Anote os resultados na Caderneta da Criança. Eles são parte do passaporte de saúde do bebê. 🌿",
    voltarPara: { label: "Cuidados com o Bebê", href: "/cuidados-bebe" },
    relacionados: [
      { slug: "vacinas", label: "Vacinas do bebê", icone: "💉" },
      { slug: "sinais-alerta", label: "Sinais de alerta", icone: "🌡️" }
    ],
    referencias: [
      { fonte: "caderneta-crianca", trecho: "Triagens Neonatais — pezinho, olhinho, orelhinha, coraçãozinho." }
    ]
  },

  "desenvolvimento-bebe": {
    slug: "desenvolvimento-bebe",
    titulo: "Marcos do desenvolvimento",
    icone: "🌱",
    resumo: "O que esperar mês a mês no primeiro ano.",
    intro:
      "Cada bebê tem o seu ritmo, mas alguns marcos ajudam a acompanhar o desenvolvimento. Se algo te preocupa, converse com o pediatra.",
    secoes: [
      {
        titulo: "Do nascimento aos 2 meses",
        itens: [
          "Reconhece e se acalma com vozes familiares.",
          "Enxerga até 20 cm — a distância do seu rosto na amamentação.",
          "Levanta brevemente a cabeça quando deitado de bruços.",
          "Sorriso reflexo dá lugar ao sorriso social por volta de 6-8 semanas."
        ]
      },
      {
        titulo: "2 a 4 meses",
        itens: [
          "Balbucia, brinca com sons, gosta quando você imita.",
          "Segura a cabeça com mais firmeza.",
          "Acompanha objetos com o olhar.",
          "Começa a perceber e interagir com brincadeiras."
        ]
      },
      {
        titulo: "4 a 6 meses",
        itens: [
          "Segura objetos com as duas mãos e leva à boca.",
          "Vira-se da barriga para as costas.",
          "Reage a sons (vira a cabeça em direção à voz).",
          "Aos 6 meses, começa o desmame com introdução alimentar."
        ]
      },
      {
        titulo: "6 a 12 meses",
        itens: [
          "Senta sem apoio (entre 6 e 8 meses).",
          "Engatinha (entre 8 e 10 meses) — alguns pulam essa etapa.",
          "Fala primeiras sílabas: 'mamã', 'papá', 'tatá'.",
          "Aponta para objetos com o dedo (em torno do 1º ano).",
          "Pode dar os primeiros passos entre 10 e 18 meses."
        ]
      },
      {
        titulo: "Sinais para conversar com o pediatra",
        itens: [
          "Não responde ao próprio nome após os 9 meses.",
          "Não aponta nem mostra objetos com 12 meses.",
          "Não anda nem sustenta o tronco com 18 meses.",
          "Perda de habilidade já adquirida em qualquer fase."
        ]
      }
    ],
    dicaSophia: "Comparar atrapalha. Cada bebê é único. Anote dúvidas e leve nas consultas. 🌿",
    voltarPara: { label: "Cuidados com o Bebê", href: "/cuidados-bebe" },
    relacionados: [
      { slug: "estimulos-seguros", label: "Estímulos seguros", icone: "🧸" },
      { slug: "alimentacao-bebe-6m", label: "Introdução alimentar", icone: "🥣" }
    ],
    referencias: [
      { fonte: "caderneta-crianca", trecho: "Marcos do Desenvolvimento — vigilância do desenvolvimento infantil." }
    ]
  },

  "alimentacao-bebe-6m": {
    slug: "alimentacao-bebe-6m",
    titulo: "Introdução alimentar (6 meses)",
    icone: "🥣",
    badge: "Saúde",
    badgeColor: "green",
    resumo: "Visão geral do Guia Alimentar do Ministério da Saúde.",
    intro:
      "Aos 6 meses, segundo o Ministério da Saúde, começa a introdução alimentar — o leite materno segue até os 2 anos ou mais. O conteúdo abaixo é uma visão geral do Guia Alimentar para Crianças Brasileiras Menores de 2 Anos. Quem orienta o que se aplica ao seu bebê (alergias, ritmo, ajustes) é o pediatra ou nutricionista.",
    secoes: [
      {
        titulo: "Como o Guia descreve o início",
        itens: [
          "A partir dos 6 meses, o Guia traz frutas, legumes, verduras, grãos, carnes e ovos como parte do cardápio.",
          "O Guia indica que peneirar e bater no liquidificador não é necessário — alimentos amassados com garfo são frequentemente lembrados.",
          "Oferecer alimentos separadamente no prato é um dos cuidados descritos pelo material oficial.",
          "Quantidades e ritmo do bebê são acompanhados pelo pediatra/nutricionista."
        ]
      },
      {
        titulo: "Esquema descrito no material oficial (referência educativa)",
        itens: [
          "Café da manhã: leite materno.",
          "Lanche da manhã: fruta + leite materno.",
          "Almoço: cereal/raiz + feijão + legume + carne ou ovo.",
          "Lanche da tarde: fruta + leite materno.",
          "Jantar: leite materno (e, conforme o desenvolvimento, refeição similar ao almoço a partir dos 9 meses).",
          "Antes de dormir: leite materno.",
          "Esse esquema é uma referência geral — adaptações são conversadas com o pediatra."
        ]
      },
      {
        titulo: "Alimentos que o Ministério da Saúde orienta evitar até os 2 anos",
        itens: [
          "Açúcar, mel, bebidas açucaradas, refrigerante, suco de caixinha.",
          "Alimentos ultraprocessados: salgadinhos, biscoitos recheados, achocolatados.",
          "Sal em excesso.",
          "Dietas restritivas (vegana estrita, sem glúten, sem lactose etc.) só com indicação e acompanhamento profissional."
        ]
      },
      {
        titulo: "Higiene e segurança alimentar",
        itens: [
          "Lavagem de mãos e utensílios antes de preparar e oferecer alimentos.",
          "Preparar próximo do horário de oferecer, com armazenamento adequado em geladeira quando preciso.",
          "Oferecer água nos intervalos das refeições.",
          "Permitir que o bebê explore alimentos com as mãos faz parte do desenvolvimento (BLW e formas mistas existem — converse com o pediatra sobre o que cabe pra vocês)."
        ]
      }
    ],
    dicaSophia:
      "Comer é descoberta. Cada bebê tem o seu ritmo — e quem afina esse ritmo com você é o pediatra. 💗",
    voltarPara: { label: "Cuidados com o Bebê", href: "/cuidados-bebe" },
    relacionados: [
      { slug: "amamentacao", label: "Amamentação", icone: "🍼" },
      { slug: "desenvolvimento-bebe", label: "Marcos do desenvolvimento", icone: "🌱" }
    ],
    referencias: [
      { fonte: "caderneta-crianca", trecho: "Alimentando para Garantir a Saúde — esquema alimentar e Guia Alimentar para Crianças Menores de 2 Anos." }
    ]
  },

  "contracepcao-pos-parto": {
    slug: "contracepcao-pos-parto",
    titulo: "Contracepção no pós-parto",
    icone: "💊",
    resumo: "Visão geral dos métodos para conversar com a ginecologista.",
    intro:
      "Mesmo amamentando exclusivamente e sem menstruar, a ovulação pode acontecer. O conteúdo abaixo é apenas educativo — a escolha do método, a indicação, o início do uso e os ajustes são feitos com sua ginecologista, considerando seu corpo, sua amamentação e seus planos.",
    secoes: [
      {
        titulo: "Métodos descritos como compatíveis com amamentação",
        itens: [
          "Preservativo (masculino ou feminino) — também previne IST.",
          "DIU (cobre ou hormonal) — quem indica e em que momento inserir é a ginecologista.",
          "Pílulas só de progesterona e injetáveis trimestrais — também avaliados caso a caso pelo médico."
        ]
      },
      {
        titulo: "Métodos descritos como pouco indicados durante o aleitamento",
        itens: [
          "Métodos hormonais combinados (estrogênio + progesterona), como pílula combinada, anel vaginal e adesivo combinados — podem interferir na produção de leite, segundo protocolos do SUS.",
          "Métodos comportamentais (como 'tabelinha') costumam ter eficácia menor enquanto o ciclo ainda não regulou."
        ]
      },
      {
        titulo: "Laqueadura",
        itens: [
          "Método definitivo — exige reflexão e conversa com a equipe e o parceiro, quando houver.",
          "Pode ser feita no momento do parto vaginal ou cesárea, conforme regras legais e indicação médica, ou de forma agendada após o puerpério.",
          "A indicação, momento e via são definidos pelo médico junto com a paciente."
        ]
      },
      {
        titulo: "Amamentação como contracepção (LAM)",
        itens: [
          "Sob condições específicas (amamentação exclusiva, em livre demanda, com amenorreia e nos primeiros 6 meses), o aleitamento oferece alguma proteção.",
          "A eficácia diminui se houver retorno da menstruação ou introdução de outros alimentos.",
          "Por isso, profissionais costumam recomendar associar outro método desde cedo — quem orienta o que cabe ao seu caso é a ginecologista."
        ]
      }
    ],
    dicaSophia:
      "Eu te ajudo a anotar perguntas pra levar pra consulta — quem decide o método com você é sua ginecologista. 💗",
    voltarPara: { label: "Pós-Parto", href: "/pos-parto" },
    relacionados: [
      { slug: "sexualidade-pos-parto", label: "Sexualidade pós-parto", icone: "💗" },
      { slug: "recuperacao-corpo", label: "Recuperação do corpo", icone: "🩸" }
    ],
    referencias: [
      { fonte: "manual-tecnico", trecho: "Atenção ao puerpério — uso de método anticoncepcional durante o aleitamento." }
    ]
  }
};

export function getTopico(slug: string) {
  return topicos[slug] ?? null;
}

export function getAllSlugs() {
  return Object.keys(topicos);
}

export function getTopicosPorPalavraChave(query: string): Topico[] {
  const q = query
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "");
  if (q.length < 3) return [];
  const palavras = q.split(/\s+/).filter((w) => w.length >= 3);
  if (palavras.length === 0) return [];

  const scored: { topico: Topico; score: number }[] = [];
  for (const topico of Object.values(topicos)) {
    const haystack = [
      topico.titulo,
      topico.resumo,
      topico.intro,
      ...topico.secoes.flatMap((s) => [s.titulo, ...s.itens])
    ]
      .join(" \n ")
      .toLowerCase()
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "");

    let score = 0;
    for (const p of palavras) {
      if (haystack.includes(p)) score += 1;
      if (
        topico.titulo
          .toLowerCase()
          .normalize("NFD")
          .replace(/[\u0300-\u036f]/g, "")
          .includes(p)
      )
        score += 2;
    }
    if (score > 0) scored.push({ topico, score });
  }

  scored.sort((a, b) => b.score - a.score);
  return scored.slice(0, 3).map((s) => s.topico);
}
