import Link from "next/link";
import { IconSparkle, IconHeart } from "@/components/Icons";

type Variant = "default" | "compact" | "chat";

type Props = {
  variant?: Variant;
};

/**
 * Aviso de transparência da Sophia.
 * Tom acolhedor, mas claro: a Sophia é uma IA de apoio educativo
 * — não substitui consulta médica/psicológica.
 */
export function DisclaimerMedico({ variant = "default" }: Props) {
  if (variant === "compact") {
    return (
      <div role="note" aria-label="Sobre a Sophia" className="ia-banner">
        <div className="ia-banner-icon">
          <IconSparkle style={{ width: 18, height: 18 }} />
        </div>
        <div>
          A <strong>Sophia</strong> é uma assistente virtual (IA) de apoio
          educativo e acolhimento. Ela não realiza consulta médica,
          psicológica, diagnóstico ou prescrição. Em emergência: SAMU 192.
          Apoio emocional 24h: CVV 188.
        </div>
      </div>
    );
  }

  if (variant === "chat") {
    return (
      <div
        role="note"
        aria-label="Sobre a Sophia"
        className="ia-banner"
        style={{ marginBottom: 14 }}
      >
        <div className="ia-banner-icon">
          <IconHeart style={{ width: 18, height: 18 }} />
        </div>
        <div>
          Aqui é um espaço de escuta e informação — a Sophia é uma IA
          carinhosa, não uma profissional de saúde. Quando precisar de
          avaliação, sua equipe (UBS, obstetra, pediatra ou psicóloga
          perinatal) vai te receber. Em emergência: SAMU 192 · Apoio
          emocional: CVV 188.
        </div>
      </div>
    );
  }

  return (
    <section role="note" aria-label="Sobre a Sophia" className="ia-banner" style={{ padding: "18px 22px", marginBottom: 18 }}>
      <div className="ia-banner-icon">
        <IconSparkle style={{ width: 20, height: 20 }} />
      </div>
      <div>
        <h4
          style={{
            margin: "0 0 6px",
            color: "#8a6a32",
            fontFamily: "var(--serif)",
            fontSize: 18
          }}
        >
          Quem é a Sophia
        </h4>
        <p style={{ margin: 0, color: "var(--texto)", fontSize: 14, lineHeight: 1.6 }}>
          A Sophia é uma <strong>assistente virtual (IA)</strong> de{" "}
          <strong>apoio educativo e acolhimento</strong> para gestação,
          parto, puerpério e cuidados com o bebê. Conteúdo baseado em
          fontes oficiais (Ministério da Saúde / SUS) e bibliografia
          reconhecida.{" "}
          <strong>
            Ela não realiza consulta médica, psicológica, diagnóstico ou
            prescrição
          </strong>{" "}
          — esses cuidados ficam com sua equipe de saúde.
        </p>
        <p style={{ margin: "10px 0 0", fontSize: 13, color: "var(--texto-suave)" }}>
          Emergência: <strong>SAMU 192</strong> · Apoio emocional 24h:{" "}
          <strong>CVV 188</strong> · Saiba mais em{" "}
          <Link href="/aviso-legal" style={{ color: "var(--rosa-forte)" }}>
            Aviso Legal
          </Link>
          .
        </p>
      </div>
    </section>
  );
}
