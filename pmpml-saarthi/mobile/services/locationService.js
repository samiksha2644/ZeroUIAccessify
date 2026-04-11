/**
 * locationService.js — GPS location helpers using expo-location.
 */

import * as Location from "expo-location";

/**
 * Request foreground location permission.
 * @returns {boolean} true if permission was granted
 */
export async function requestPermission() {
  const { status } = await Location.requestForegroundPermissionsAsync();
  return status === "granted";
}

/**
 * Get the user's current position (foreground, high accuracy).
 * @returns {{ latitude: number, longitude: number } | null}
 */
export async function getCurrentLocation() {
  try {
    const granted = await requestPermission();
    if (!granted) {
      console.warn("Location permission not granted");
      return null;
    }

    const location = await Location.getCurrentPositionAsync({
      accuracy: Location.Accuracy.High,
    });

    return {
      latitude: location.coords.latitude,
      longitude: location.coords.longitude,
    };
  } catch (err) {
    console.error("getCurrentLocation error:", err);
    return null;
  }
}

/**
 * Start watching the user's position at a given interval.
 * @param {function} callback - Called with { latitude, longitude } on each update
 * @param {number} intervalMs - Minimum time between updates in ms (default 5000)
 * @returns {object} subscription — call subscription.remove() to stop
 */
export async function watchLocation(callback, intervalMs = 5000) {
  const granted = await requestPermission();
  if (!granted) {
    console.warn("Location permission not granted for watch");
    return null;
  }

  const subscription = await Location.watchPositionAsync(
    {
      accuracy: Location.Accuracy.High,
      timeInterval: intervalMs,
      distanceInterval: 10, // minimum 10 meters between updates
    },
    (location) => {
      callback({
        latitude: location.coords.latitude,
        longitude: location.coords.longitude,
      });
    }
  );

  return subscription;
}
