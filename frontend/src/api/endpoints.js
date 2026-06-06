import api from './client';

// Auth
export const login = (email, password) => {
  const form = new URLSearchParams();
  form.append('username', email);
  form.append('password', password);
  return api.post('/auth/login', form);
};
export const register = (data) => api.post('/auth/register', data);

// Suppliers
export const getSuppliers = () => api.get('/suppliers/');
export const createSupplier = (data) => api.post('/suppliers/', data);
export const updateSupplier = (id, data) => api.put(`/suppliers/${id}`, data);
export const deleteSupplier = (id) => api.delete(`/suppliers/${id}`);

// Products
export const getProducts = () => api.get('/products/');
export const createProduct = (data) => api.post('/products/', data);

// Warehouses
export const getWarehouses = () => api.get('/warehouses/');
export const createWarehouse = (data) => api.post('/warehouses/', data);

// Inventory
export const getInventory = () => api.get('/inventory/');
export const createInventory = (data) => api.post('/inventory/', data);

// Simulations
export const runSimulation = (data) => api.post('/simulations/run', data);
export const getSimulations = () => api.get('/simulations/');
export const getSimulation = (id) => api.get(`/simulations/${id}`);
