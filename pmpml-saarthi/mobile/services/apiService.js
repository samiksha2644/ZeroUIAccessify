/**
 * apiService.js — Axios wrapper for the FastAPI backend.
 */

import axios from "axios";

// Default to localhost; override in .env or app.json extra
const BASE_URL = process.env.EXPO_PUBLIC_BACKEND_URL || "http://10.0.2.2:8000";

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 10000,
  headers: { "Content-Type": "application/json" },
});

/**
 * POST /parse-destination
 * @param {string} text - Raw transcribed voice text
 * @returns {{ destination: string|null, command: string|null }}
 */
export async function parseDestination(text) {
  const { data } = await api.post("/parse-destination", { text });
  return data;
}

/**
 * POST /find-route
 * @param {number} userLat
 * @param {number} userLng
 * @param {string} destinationName
 * @returns {RouteResponse}
 */
export async function findRoute(userLat, userLng, destinationName) {
  const { data } = await api.post("/find-route", {
    user_lat: userLat,
    user_lng: userLng,
    destination_name: destinationName,
  });
  return data;
}

/**
 * POST /check-proximity
 * @param {number} userLat
 * @param {number} userLng
 * @param {number} targetLat
 * @param {number} targetLng
 * @returns {{ distance_meters: number, alert: boolean, message: string }}
 */
export async function checkProximity(userLat, userLng, targetLat, targetLng) {
  const { data } = await api.post("/check-proximity", {
    user_lat: userLat,
    user_lng: userLng,
    target_stop_lat: targetLat,
    target_stop_lng: targetLng,
  });
  return data;
}

export default api;
