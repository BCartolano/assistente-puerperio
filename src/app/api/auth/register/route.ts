import bcrypt from "bcryptjs";
import { NextResponse } from "next/server";
import { z } from "zod";
import { prisma } from "@/lib/prisma";
import { addHours, generateToken } from "@/lib/tokens";
import { sendVerificationEmail } from "@/lib/mailer";

const schema = z.object({
  name: z.string().min(2),
  email: z.email(),
  password: z.string().min(6)
});

export async function POST(req: Request) {
  const parsed = schema.safeParse(await req.json());
  if (!parsed.success) {
    return NextResponse.json({ error: "Dados invalidos." }, { status: 400 });
  }

  const { name, email, password } = parsed.data;
  const existing = await prisma.user.findUnique({ where: { email } });
  if (existing) {
    return NextResponse.json({ error: "E-mail ja cadastrado." }, { status: 409 });
  }

  const passwordHash = await bcrypt.hash(password, 10);
  const user = await prisma.user.create({
    data: { name, email, passwordHash }
  });

  const token = generateToken();
  await prisma.verifyToken.create({
    data: {
      token,
      userId: user.id,
      expiresAt: addHours(new Date(), 24)
    }
  });
  try {
    await sendVerificationEmail(user.email, token);
  } catch (error) {
    const message = error instanceof Error ? error.message : "Falha desconhecida";
    return NextResponse.json(
      { error: `Conta criada, mas o e-mail de verificação não foi enviado. Motivo: ${message}` },
      { status: 502 }
    );
  }

  return NextResponse.json({
    message: "Conta criada. Verifique seu e-mail para ativar o acesso."
  });
}
