import { NextResponse } from "next/server";
import { z } from "zod";
import { prisma } from "@/lib/prisma";
import { addHours, generateToken } from "@/lib/tokens";
import { sendVerificationEmail } from "@/lib/mailer";

const schema = z.object({ email: z.email() });

export async function POST(req: Request) {
  const parsed = schema.safeParse(await req.json());
  if (!parsed.success) {
    return NextResponse.json({ error: "E-mail invalido." }, { status: 400 });
  }

  const user = await prisma.user.findUnique({ where: { email: parsed.data.email } });
  if (!user) {
    return NextResponse.json({ message: "Se o e-mail existir, enviaremos novamente." });
  }
  if (user.emailVerified) {
    return NextResponse.json({ message: "E-mail ja confirmado." });
  }

  const token = generateToken();
  await prisma.verifyToken.create({
    data: { token, userId: user.id, expiresAt: addHours(new Date(), 24) }
  });
  try {
    await sendVerificationEmail(user.email, token);
  } catch (error) {
    const message = error instanceof Error ? error.message : "Falha desconhecida";
    return NextResponse.json({ error: `Falha ao reenviar verificação. ${message}` }, { status: 502 });
  }

  return NextResponse.json({ message: "Novo e-mail de verificacao enviado." });
}
