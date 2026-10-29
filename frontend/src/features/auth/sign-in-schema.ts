import { z } from "zod";

const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export const signInSchema = z.object({
  email: z
    .string()
    .trim()
    .min(1, "Enter your email address.")
    .regex(emailPattern, "Enter a valid email address."),
  password: z.string().min(1, "Enter your password."),
  rememberMe: z.boolean(),
});

export type SignInValues = z.infer<typeof signInSchema>;
