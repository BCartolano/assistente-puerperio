import { NextResponse } from "next/server";
import { z } from "zod";
import { prisma } from "@/lib/prisma";
import { addHours, generateToken } from "@/lib/tokens";
import { sendResetPasswordEmail } from "@/lib/mailer";

const schema = z.object({ email: z.email() });

export async function POST(req: Request) {
  const parsed = schema.safeParse(await req.json());
  if (!parsed.success) {
    return NextResponse.json({ error: "E-mail invalido." }, { status: 400 });
  }

  const user = await prisma.user.findUnique({ where: { email: parsed.data.email } });
  if (user) {
    const token = generateToken();
    await prisma.passwordResetToken.create({
      data: {
        token,
        userId: user.id,
        expiresAt: addHours(new Date(), 1)
      }
    });
    try {
      await sendResetPasswordEmail(user.email, token);
    } catch (error) {
      const message = error instanceof Error ? error.message : "Falha desconhecida";
      return NextResponse.json({ error: `Não foi possível enviar o e-mail de reset. ${message}` }, { status: 502 });
    }
  }

  return NextResponse.json({
    message: "Se o e-mail existir, enviaremos um link de redefinicao."
  });
}
