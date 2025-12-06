// frontend_tracked/src/api.js
import axios from "axios";

const API_BASE = process.env.REACT_APP_API_BASE || ""; // will be set in Vercel
const client = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
});

export default client;
