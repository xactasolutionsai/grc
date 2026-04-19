const API_BASE = '/fe-api/users';

export const getUsers = async () => {
    const response = await fetch(`${API_BASE}/`);
    if (!response.ok) throw new Error('Failed to fetch users');
    return response.json();
};
