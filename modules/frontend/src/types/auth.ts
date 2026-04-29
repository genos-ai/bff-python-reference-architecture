export interface User {
  id: string;
  email: string;
  display_name: string | null;
}

export interface AuthResponse {
  access_token: string;
  sse_token: string;
  token_type: string;
  user: User;
}
