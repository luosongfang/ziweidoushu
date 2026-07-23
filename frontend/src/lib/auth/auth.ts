/** @deprecated 使用 authService.ts */
export {
  signUpWithEmail,
  signInWithEmail,
  signOut,
  signInWithWechat,
  signInWithPhone,
  getAuthMode,
  getAuthSessionRaw,
  clearDevSession,
  login,
  logout,
  register,
  registerWithEmail,
  loginWithEmail,
} from "@/lib/auth/authService";
export type { AuthMode, RegisterInput, LoginInput } from "@/lib/auth/authService";
