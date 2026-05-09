"use client";

import Link from "next/link";
import { FormEvent, useEffect, useRef, useState } from "react";
import { getTopicosPorPalavraChave, type Topico } from "@/lib/topicos";
import { DisclaimerMedico } from "@/components/DisclaimerMedico";
import { SophiaAvatar } from "@/components/SophiaAvatar";
import {
  IconPaperPlane,
  IconHeart,
  IconArrowRight,
  IconHands
} from "@/components/Icons";

type ResponsePart =
  | { type: "text"; text: string }
  | { type: "topico"; topico: Topico }
  | { type: "cuidado-suave" };

type Message = {
  id: string;
  author: "bot" | "user";
  parts: ResponsePart[];
  time: string;
};

const greetings: Message[] = [
  {
    id: "greet-1",
    author: "bot",
    parts: [
      {
        type: "text",
        text:
          "Oi, mamãe. Que bom que você veio. Eu sou a Sophia, e estou aqui pra te escutar com calma e carinho.\n\nPode me contar como o seu coração está hoje? Se quiser começar pelo que está pesando, ou pelo que está bonito — qualquer caminho serve. Eu te acompanho."
      }
    ],
    time: nowLabel()
  }
];

const quickReplies = [
  "Estou cansada",
  "Tô feliz hoje",
  "Preciso desabafar",
  "Dúvida sobre amamentação",
  "Tô preocupada com algo"
];

/**
 * Respostas emocionais — todas com tom acolhedor, sem frases robóticas.
 * Nada de "eu não dou diagnóstico" ou "procure uma equipe", essas mensagens
 * foram retiradas a pedido. A Sophia primeiro acolhe; quando algo de saúde
 * surge, ela usa um cartão de cuidado suave (não uma sentença fria).
 */
const respostasEmocionais: { palavras: string[]; texto: string }[] = [
  {
    palavras: ["cansada", "cansado", "exausta", "sem dormir", "esgotada", "sem energia", "sem forca", "sem força"],
    texto:
      "Eu te ouço. Esse cansaço é de quem ama muito e ainda assim segue acordando, segue cuidando — e o seu corpo está pedindo um colo. Você merece encostar a cabeça em algum lugar agora, mesmo que seja só por cinco minutos.\n\nQuer que eu fique com você um pouquinho? Posso te trazer leituras leves sobre sono e descanso, no seu tempo."
  },
  {
    palavras: ["triste", "tristeza", "chorando", "deprimida", "sem vontade", "vazia", "vazio", "chorar"],
    texto:
      "Vem cá, respira comigo. A sua tristeza tem lugar aqui — não precisa explicar, não precisa se desculpar. Sentir isso não te faz uma mãe pior; te faz humana.\n\nFica comigo, vamos com calma. Posso te oferecer algumas leituras gentis sobre o que pode estar acontecendo e o que costuma trazer alívio."
  },
  {
    palavras: ["ansiedade", "ansiosa", "medo", "panico", "pânico", "angustia", "angústia", "angustiada", "agoniada"],
    texto:
      "A ansiedade quando aperta parece que vai te engolir, eu sei. Vamos juntas: respira fundo agora, segura por 4, solta devagar pela boca. Outra vez.\n\nVocê está aqui, comigo, no presente. Quer que eu te guie por cinco minutos de respiração e depois a gente conversa sobre o que está apertando?"
  },
  {
    palavras: ["culpa", "culpada", "ruim", "pessima mae", "péssima mãe", "fracassei", "fracasso", "nao sirvo", "não sirvo"],
    texto:
      "Para. Olha pra mim. Você não é uma mãe ruim. Mãe ruim não pensa nisso, mãe ruim não se preocupa. Quem se cobra desse jeito é mãe que ama demais e está exausta.\n\nVem ler comigo sobre autocompaixão — não pra te corrigir, mas pra te lembrar de quem você realmente é."
  },
  {
    palavras: ["feliz", "amando", "felicidade", "encantada", "apaixonada", "alegre"],
    texto:
      "Que delícia ouvir isso, mamãe. Esses momentos lindos também merecem ser registrados — porque o puerpério tem muito amor escondido entre os dias difíceis. Quer guardar isso num diário, ou ler sobre vínculo? Te trago algo carinhoso."
  },
  {
    palavras: ["sozinha", "ninguem me ajuda", "ninguém me ajuda", "sem ajuda", "abandonada", "isolada", "ninguem", "ninguém"],
    texto:
      "Eu te escuto. Estar sozinha não é pra ser uma fase, é pra ser temporário — e existe um caminho pra construir colo, mesmo quando parece que não tem ninguém. Vou ficar aqui contigo, e a gente conversa sobre como começar a tecer essa rede, sem pressa."
  },
  {
    palavras: ["sobrecarregada", "sobrecarga", "nao aguento", "nao dou conta", "não dou conta", "transbordando"],
    texto:
      "Faz sentido você estar transbordando. Você está fazendo muita coisa — mais do que qualquer corpo deveria carregar sozinho. Vem comigo respirar um pouco, e depois a gente vê juntas o que dá pra delegar, pra adiar, pra soltar. Não precisa carregar tudo."
  }
];

// Crise — sempre encaminha pros canais de ajuda especializada, mas com calor.
const palavrasCrise = [
  "machuca",
  "fazer mal",
  "morrer",
  "suicídio",
  "suicidio",
  "me matar",
  "não aguento mais",
  "nao aguento mais",
  "sem saída",
  "sem saida",
  "acabar comigo",
  "desaparecer",
  "sumir do mundo"
];

const respostaCrise =
  "Você está sentindo algo muito pesado agora — e eu fico de coração apertado por você ter buscado um lugar pra dizer. Eu te escuto.\n\nQuero pedir uma coisa muito importante, com muito carinho: liga agora pro CVV no 188. É gratuito, sigiloso, 24h, e tem alguém pronto pra ficar com você no telefone. Se houver risco imediato, vá ao pronto-socorro mais próximo ou ligue 192 (SAMU).\n\nEnquanto você liga ou enquanto você se prepara, eu fico aqui. Não vai ficar sozinha. Você é importante — e essa fase, mesmo desse jeito, vai mudar.";

// Palavras que sugerem queixa de saúde — Sophia acolhe e oferece um cartão de cuidado suave.
const palavrasQueixaSaude = [
  "dor",
  "dói",
  "doi",
  "doendo",
  "sangramento",
  "sangrando",
  "febre",
  "vomito",
  "vômito",
  "vomitando",
  "diarreia",
  "diarréia",
  "infecção",
  "infeccao",
  "pus",
  "remédio",
  "remedio",
  "medicamento",
  "antibiotico",
  "antibiótico",
  "anticoncepcional",
  "pílula",
  "pilula",
  "dose",
  "dosagem",
  "sintoma",
  "sintomas",
  "tontura",
  "desmaio",
  "convulsão",
  "convulsao",
  "pressao alta",
  "pressão alta",
  "alergia",
  "mastite",
  "fissura",
  "rachadura"
];

const respostaFallbackAcolhe =
  "Tô aqui, ouvindo você. Conta um pouquinho mais, no seu tempo — sem pressa, sem precisar arrumar as palavras. Se quiser, posso te trazer alguma leitura gentil sobre o tema que está te tocando hoje.";

function nowLabel() {
  return new Date().toLocaleTimeString("pt-BR", {
    hour: "2-digit",
    minute: "2-digit"
  });
}

function normalizar(texto: string) {
  return texto
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "");
}

function detectarCrise(input: string) {
  const lower = normalizar(input);
  return palavrasCrise.some((p) => lower.includes(normalizar(p)));
}

function detectarQueixaSaude(input: string) {
  const lower = normalizar(input);
  return palavrasQueixaSaude.some((p) => lower.includes(normalizar(p)));
}

function detectarRespostaEmocional(input: string) {
  const lower = normalizar(input);
  for (const r of respostasEmocionais) {
    for (const p of r.palavras) {
      if (lower.includes(normalizar(p))) return r;
    }
  }
  return null;
}

function gerarResposta(input: string): ResponsePart[] {
  const parts: ResponsePart[] = [];

  if (detectarCrise(input)) {
    parts.push({ type: "text", text: respostaCrise });
    const sugestoes = getTopicosPorPalavraChave("baby blues depressao ajuda");
    for (const t of sugestoes.slice(0, 2)) {
      parts.push({ type: "topico", topico: t });
    }
    return parts;
  }

  const emocional = detectarRespostaEmocional(input);
  const topicosRelevantes = getTopicosPorPalavraChave(input);
  const queixaSaude = detectarQueixaSaude(input);

  if (emocional) {
    parts.push({ type: "text", text: emocional.texto });
  } else if (topicosRelevantes.length > 0) {
    parts.push({
      type: "text",
      text:
        "Separei aqui um conteúdo carinhoso, no estilo leitura de cabeceira — é pra você ler com calma, no seu tempo:"
    });
  }

  if (topicosRelevantes.length > 0) {
    for (const t of topicosRelevantes.slice(0, 3)) {
      parts.push({ type: "topico", topico: t });
    }
  }

  if (queixaSaude) {
    parts.push({ type: "cuidado-suave" });
  }

  if (parts.length === 0) {
    parts.push({ type: "text", text: respostaFallbackAcolhe });
  } else if (!emocional && topicosRelevantes.length === 0 && !queixaSaude) {
    parts.push({ type: "text", text: respostaFallbackAcolhe });
  }

  return parts;
}

export function ChatSophia() {
  const [messages, setMessages] = useState<Message[]>(greetings);
  const [input, setInput] = useState("");
  const windowRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (windowRef.current) {
      windowRef.current.scrollTop = windowRef.current.scrollHeight;
    }
  }, [messages]);

  function send(text: string) {
    const clean = text.trim();
    if (!clean) return;
    const userMsg: Message = {
      id: crypto.randomUUID(),
      author: "user",
      parts: [{ type: "text", text: clean }],
      time: nowLabel()
    };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");

    setTimeout(() => {
      const botMsg: Message = {
        id: crypto.randomUUID(),
        author: "bot",
        parts: gerarResposta(clean),
        time: nowLabel()
      };
      setMessages((prev) => [...prev, botMsg]);
    }, 500);
  }

  function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    send(input);
  }

  return (
    <div className="chat-shell">
      <div className="chat-header">
        <SophiaAvatar size="sm" className="chat-avatar" />
        <div>
          <strong>Sophia</strong>
          <p style={{ margin: "2px 0 0", fontSize: 12.5 }}>
            <span className="chat-status">acolhendo você agora</span>
          </p>
        </div>
      </div>

      <DisclaimerMedico variant="chat" />

      <div className="chat-window" ref={windowRef}>
        {messages.map((m) => (
          <div key={m.id} className={`chat-bubble ${m.author}`}>
            {m.parts.map((part, i) => {
              if (part.type === "text") {
                return (
                  <div key={i} style={{ whiteSpace: "pre-wrap" }}>
                    {part.text}
                  </div>
                );
              }

              if (part.type === "cuidado-suave") {
                return (
                  <div key={i} className="chat-cuidado" role="note">
                    <strong style={{ color: "#8a6a32", display: "inline-flex", alignItems: "center", gap: 6 }}>
                      <IconHands style={{ width: 16, height: 16 }} />
                      Um cuidado a mais
                    </strong>
                    <div style={{ marginTop: 4 }}>
                      O que você me contou pode pedir um olhar mais de pertinho.
                      Quando você puder, vale levar isso pra sua equipe — UBS,
                      obstetra ou pediatra do bebê. Eu fico aqui, do seu lado,
                      até você conseguir esse encontro. Em emergência:{" "}
                      <strong>SAMU 192</strong>. Apoio emocional 24h:{" "}
                      <strong>CVV 188</strong>.
                    </div>
                  </div>
                );
              }

              return (
                <Link key={i} href={`/conteudo/${part.topico.slug}`} className="chat-card">
                  <span className="chat-card-icon" aria-hidden>
                    <IconHeart />
                  </span>
                  <span style={{ flex: 1 }}>
                    <strong>{part.topico.titulo}</strong>
                    <span className="chat-card-desc">{part.topico.resumo}</span>
                  </span>
                  <IconArrowRight style={{ width: 16, height: 16, color: "var(--rosa-forte)" }} />
                </Link>
              );
            })}
            <div className="chat-time">{m.time}</div>
          </div>
        ))}
      </div>

      <div className="chat-quick">
        {quickReplies.map((q) => (
          <button key={q} type="button" onClick={() => send(q)}>
            {q}
          </button>
        ))}
      </div>

      <form className="chat-input-wrap" onSubmit={handleSubmit}>
        <input
          className="chat-input"
          placeholder="Escreve pra mim, sem pressa..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          aria-label="Mensagem para a Sophia"
        />
        <button type="submit" className="chat-send" aria-label="Enviar">
          <IconPaperPlane />
          Enviar
        </button>
      </form>
    </div>
  );
}
