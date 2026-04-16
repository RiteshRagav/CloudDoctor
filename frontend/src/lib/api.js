import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const api = axios.create({
  baseURL: API,
  timeout: 60000,
  headers: {
    "Content-Type": "application/json",
  },
});

// Health
export const getHealth = () => api.get("/health");

// Incidents
export const triggerIncident = (scenario) =>
  api.post("/incidents/trigger", { scenario });
export const getIncidents = (status) =>
  api.get("/incidents", { params: status ? { status } : {} });
export const getIncident = (id) => api.get(`/incidents/${id}`);
export const diagnoseIncident = (id) => api.post(`/incidents/${id}/diagnose`);
export const resolveIncident = (id) => api.post(`/incidents/${id}/resolve`);

// Logs
export const getLogs = (params = {}) => api.get("/logs", { params });
export const getLogStats = (since) =>
  api.get("/logs/stats", { params: since ? { since } : {} });

// Simulator
export const getSimulatorState = () => api.get("/simulator/state");
export const stopSimulator = () => api.post("/simulator/stop");
export const getScenarios = () => api.get("/scenarios");

export default api;
