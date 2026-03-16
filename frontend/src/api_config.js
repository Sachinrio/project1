/**
 * Central API configuration for connecting frontend to backend.
 * On Render/Production: Use VITE_API_URL environment variable.
 * On Local: Use the Vite proxy (/api).
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || ''; 

export const API_ENDPOINTS = {
  EVENTS: `${API_BASE_URL}/api/v1/events`,
  AUTH_ME: `${API_BASE_URL}/api/v1/auth/me`,
  LOGIN: `${API_BASE_URL}/api/v1/auth/login`,
  REGISTER: `${API_BASE_URL}/api/v1/auth/register`,
  FORGOT_PASSWORD: `${API_BASE_URL}/api/v1/auth/forgot-password`,
  RESET_PASSWORD: `${API_BASE_URL}/api/v1/auth/reset-password`,
  GOOGLE_AUTH: `${API_BASE_URL}/api/v1/auth/google`,
  VERIFY_EMAIL_SEND: `${API_BASE_URL}/api/v1/auth/verify-email/send`,
  VERIFY_EMAIL_CHECK: `${API_BASE_URL}/api/v1/auth/verify-email/check`,
  CHAT: `${API_BASE_URL}/api/chat`,
};

export default API_BASE_URL;
