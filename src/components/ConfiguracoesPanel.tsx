"use client";

import Link from "next/link";
import { useState } from "react";
import {
  IconUser,
  IconMail,
  IconLock,
  IconBell,
  IconHeart,
  IconShield,
  IconArrowRight
} from "@/components/Icons";

type Settings = {
  notifPush: boolean;
  notifEmail: boolean;
  reminders: boolean;
  newsletter: boolean;
};

export function ConfiguracoesPanel({ name, email }: { name: string; email: string }) {
  const [settings, setSettings] = useState<Settings>({
    notifPush: true,
    notifEmail: true,
    reminders: true,
    newsletter: false
  });

  function toggle(key: keyof Settings) {
    setSettings((prev) => ({ ...prev, [key]: !prev[key] }));
  }

  const items: { key: keyof Settings; title: string; desc: string }[] = [
    { key: "notifPush", title: "Notificações no celular", desc: "Lembretes gentis durante o dia." },
    { key: "notifEmail", title: "E-mails da Sophia", desc: "Resumo semanal e novidades selecionadas." },
    { key: "reminders", title: "Check-in emocional diário", desc: "Pequena pausa de 1 minuto pra você." },
    { key: "newsletter", title: "Boletim mensal", desc: "Conteúdos novos do mês, sem spam." }
  ];

  return (
    <>
      <section className="page-section">
        <h2 className="page-title">Conta</h2>
        <p className="page-subtitle">Suas informações principais.</p>

        <div className="list-stack" style={{ marginTop: 18 }}>
          <article className="list-row">
            <div className="list-icon"><IconUser /></div>
            <div className="list-text">
              <h4>Nome</h4>
              <p>{name}</p>
            </div>
            <Link href="/meu-perfil" className="list-action">
              Editar <IconArrowRight style={{ width: 14, height: 14, display: "inline", verticalAlign: "middle" }} />
            </Link>
          </article>

          <article className="list-row green">
            <div className="list-icon"><IconMail /></div>
            <div className="list-text">
              <h4>E-mail</h4>
              <p>{email}</p>
            </div>
            <Link href="/meu-perfil" className="list-action">
              Editar <IconArrowRight style={{ width: 14, height: 14, display: "inline", verticalAlign: "middle" }} />
            </Link>
          </article>

          <article className="list-row">
            <div className="list-icon"><IconLock /></div>
            <div className="list-text">
              <h4>Senha</h4>
              <p>Mantenha sua conta segura.</p>
            </div>
            <Link href="/mudar-senha" className="list-action">
              Mudar senha <IconArrowRight style={{ width: 14, height: 14, display: "inline", verticalAlign: "middle" }} />
            </Link>
          </article>
        </div>
      </section>

      <section className="page-section">
        <h2 className="page-title">Preferências</h2>
        <p className="page-subtitle">Você no controle: ligue só o que faz sentido pra você.</p>

        <div className="list-stack" style={{ marginTop: 18 }}>
          {items.map((item) => (
            <article key={item.key} className="list-row">
              <div className="list-icon"><IconBell /></div>
              <div className="list-text">
                <h4>{item.title}</h4>
                <p>{item.desc}</p>
              </div>
              <label className="toggle">
                <input type="checkbox" checked={settings[item.key]} onChange={() => toggle(item.key)} />
                <span className="toggle-slider" />
              </label>
            </article>
          ))}
        </div>
      </section>

      <section className="page-section">
        <h2 className="page-title">Privacidade e dados</h2>
        <p className="page-subtitle">Tudo o que tem a ver com seus dados, num só lugar.</p>
        <div className="list-stack" style={{ marginTop: 18 }}>
          <article className="list-row">
            <div className="list-icon"><IconShield /></div>
            <div className="list-text">
              <h4>Política de Privacidade</h4>
              <p>Como cuido das suas informações, em linguagem leve.</p>
            </div>
            <Link href="/privacidade" className="list-action">
              Abrir <IconArrowRight style={{ width: 14, height: 14, display: "inline", verticalAlign: "middle" }} />
            </Link>
          </article>
          <article className="list-row green">
            <div className="list-icon"><IconHeart /></div>
            <div className="list-text">
              <h4>Gerenciar consentimento</h4>
              <p>Ative ou desative as finalidades de uso dos seus dados.</p>
            </div>
            <Link href="/consentimento" className="list-action">
              Abrir <IconArrowRight style={{ width: 14, height: 14, display: "inline", verticalAlign: "middle" }} />
            </Link>
          </article>
          <article className="list-row">
            <div className="list-icon" style={{ background: "#fff5e6", color: "#a06a32" }}>
              <IconShield />
            </div>
            <div className="list-text">
              <h4>Excluir meus dados</h4>
              <p>Apagar sua conta e tudo o que está com a gente.</p>
            </div>
            <Link href="/excluir-meus-dados" className="list-action">
              Abrir <IconArrowRight style={{ width: 14, height: 14, display: "inline", verticalAlign: "middle" }} />
            </Link>
          </article>
        </div>
      </section>
    </>
  );
}
