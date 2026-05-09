import { Resend } from "resend";

const resendApiKey = process.env.RESEND_API_KEY;

const resend = resendApiKey ? new Resend(resendApiKey) : null;

export async function sendVerificationEmail(email: string, token: string) {
  if (!resend) {
    throw new Error("RESEND_API_KEY não configurada.");
  }
  const url = `${process.env.APP_BASE_URL}/verify-email?token=${token}`;

  const response = await resend.emails.send({
    from: "Sophia <onboarding@resend.dev>",
    to: email,
    subject: "Confirme seu e-mail - Sophia",
    html: `
      <div style="margin:0;padding:24px;background:#f8f3f6;font-family:Arial,sans-serif;color:#2f2b33;">
        <table width="100%" cellpadding="0" cellspacing="0" role="presentation" style="max-width:560px;margin:0 auto;background:#ffffff;border:1px solid #f1e3eb;border-radius:14px;padding:28px;">
          <tr>
            <td>
              <p style="margin:0 0 8px 0;color:#9a89a0;font-size:14px;">Sophia</p>
              <h1 style="margin:0 0 14px 0;font-size:26px;line-height:1.2;color:#2f2b33;">Bem-vinda</h1>
              <p style="margin:0 0 20px 0;font-size:16px;line-height:1.5;">
                Estamos felizes em ter voce aqui. Para ativar seu acesso, confirme seu e-mail:
              </p>
              <p style="margin:0 0 20px 0;">
                <a href="${url}" style="display:inline-block;background:#f59cc1;color:#ffffff;text-decoration:none;font-weight:700;padding:12px 20px;border-radius:8px;">
                  Confirmar e-mail
                </a>
              </p>
              <p style="margin:0 0 6px 0;font-size:13px;color:#7a6f80;line-height:1.5;">
                Se o botao nao funcionar, copie e cole este link no navegador:
              </p>
              <p style="margin:0;font-size:13px;word-break:break-all;color:#7a6f80;line-height:1.5;">
                <a href="${url}" style="color:#7a6f80;">${url}</a>
              </p>
            </td>
          </tr>
        </table>
      </div>
    `,
    text: `Bem-vinda a Sophia!\n\nPara ativar seu acesso, confirme seu e-mail: ${url}`
  });

  if (response.error) {
    throw new Error(`Falha ao enviar e-mail de verificação: ${response.error.message}`);
  }
}

export async function sendResetPasswordEmail(email: string, token: string) {
  if (!resend) {
    throw new Error("RESEND_API_KEY não configurada.");
  }
  const url = `${process.env.APP_BASE_URL}/reset-password?token=${token}`;

  const response = await resend.emails.send({
    from: "Sophia <onboarding@resend.dev>",
    to: email,
    subject: "Redefinição de senha - Sophia",
    html: `
      <div style="margin:0;padding:24px;background:#f8f3f6;font-family:Arial,sans-serif;color:#2f2b33;">
        <table width="100%" cellpadding="0" cellspacing="0" role="presentation" style="max-width:560px;margin:0 auto;background:#ffffff;border:1px solid #f1e3eb;border-radius:14px;padding:28px;">
          <tr>
            <td>
              <p style="margin:0 0 8px 0;color:#9a89a0;font-size:14px;">Sophia</p>
              <h1 style="margin:0 0 14px 0;font-size:26px;line-height:1.2;color:#2f2b33;">Redefinir senha</h1>
              <p style="margin:0 0 20px 0;font-size:16px;line-height:1.5;">
                Recebemos um pedido para redefinir sua senha. Clique no botao abaixo para continuar:
              </p>
              <p style="margin:0 0 20px 0;">
                <a href="${url}" style="display:inline-block;background:#f59cc1;color:#ffffff;text-decoration:none;font-weight:700;padding:12px 20px;border-radius:8px;">
                  Redefinir senha
                </a>
              </p>
              <p style="margin:0 0 6px 0;font-size:13px;color:#7a6f80;line-height:1.5;">
                Se o botao nao funcionar, copie e cole este link no navegador:
              </p>
              <p style="margin:0;font-size:13px;word-break:break-all;color:#7a6f80;line-height:1.5;">
                <a href="${url}" style="color:#7a6f80;">${url}</a>
              </p>
            </td>
          </tr>
        </table>
      </div>
    `,
    text: `Redefinir senha\n\nClique no link para criar uma nova senha: ${url}`
  });

  if (response.error) {
    throw new Error(`Falha ao enviar e-mail de reset: ${response.error.message}`);
  }
}
