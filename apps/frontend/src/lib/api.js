const BASE = "http://127.0.0.1:8080/api";

const jsonHeaders = (token) => ({
  'Content-Type': 'application/json',
  ...(token && { 'Authorization': `Bearer ${token}` }),
});

class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.status = status;
  }
}

const request = async (path, options = {}) => {
  const res = await fetch(`${BASE}${path}`, options);
  if (res.status === 204) return null;
  const body = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new ApiError(body.error || body.message || `오류 (${res.status})`, res.status);
  }
  return body;
};

export { ApiError };

export const authAPI = {
  login: (email, password) =>
    request('/auth/login', {
      method: 'POST',
      headers: jsonHeaders(),
      body: JSON.stringify({ email, password }),
    }),

  register: (data) =>
    request('/auth/register', {
      method: 'POST',
      headers: jsonHeaders(),
      body: JSON.stringify(data),
    }),

  getProfile: (token) =>
    request('/auth/profile', { headers: jsonHeaders(token) }),

  updateProfile: (token, data) =>
    request('/auth/profile', {
      method: 'PATCH',
      headers: jsonHeaders(token),
      body: JSON.stringify(data),
    }),

  updateProfileImage: (token, formData) =>
    request('/auth/profile/image', {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}` },
      body: formData,
    }),

  forgotPassword: (email) =>
    request('/auth/forgot-password', {
      method: 'POST',
      headers: jsonHeaders(),
      body: JSON.stringify({ email }),
    }),
};

export const tripAPI = {
  plan: (data, signal) =>
    request('/trip/plan', {
      method: 'POST',
      headers: jsonHeaders(),
      body: JSON.stringify(data),
      signal,
    }),

  save: (token, data) =>
    request('/trip/save', {
      method: 'POST',
      headers: jsonHeaders(token),
      body: JSON.stringify(data),
    }),

  getAll: (token) =>
    request('/trip/saved', { headers: jsonHeaders(token) }),

  getOne: (token, id) =>
    request(`/trip/saved/${id}`, { headers: jsonHeaders(token) }),

  update: (token, id, data) =>
    request(`/trip/saved/${id}`, {
      method: 'PATCH',
      headers: jsonHeaders(token),
      body: JSON.stringify(data),
    }),

  delete: (token, id) =>
    request(`/trip/saved/${id}`, {
      method: 'DELETE',
      headers: jsonHeaders(token),
    }),
};
