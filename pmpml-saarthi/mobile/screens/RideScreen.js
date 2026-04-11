/**
 * RideScreen.js — Active ride tracker.
 *
 * Receives { routeData } via route params.
 * Continuously polls GPS and checks proximity to the destination stop.
 * Alerts the user 1 stop before and at the destination.
 */

import React, { useEffect, useState, useRef } from "react";
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  StatusBar,
  Vibration,
} from "react-native";
import { speak, stopSpeaking } from "../services/voiceService";
import { checkProximity } from "../services/apiService";
import { watchLocation } from "../services/locationService";

export default function RideScreen({ route, navigation }) {
  const { routeData } = route.params;
  const [currentStopIndex, setCurrentStopIndex] = useState(0);
  const [distanceToDestination, setDistanceToDestination] = useState(null);
  const [status, setStatus] = useState("Ride in progress");
  const [arrived, setArrived] = useState(false);
  const [alertedPenultimate, setAlertedPenultimate] = useState(false);
  const [alertedArrival, setAlertedArrival] = useState(false);
  const subscriptionRef = useRef(null);
  const stopsOnJourney = routeData.stops_on_journey || [];
  const totalStops = routeData.total_stops || stopsOnJourney.length - 1;
  const destStop = routeData.destination_stop;

  useEffect(() => {
    let isMounted = true;

    const init = async () => {
      await speak(
        `Ride started. You are heading to ${destStop.name}. ${totalStops} stops remaining. I will alert you before your stop.`
      );

      // Start GPS watch
      const sub = await watchLocation(async (loc) => {
        if (!isMounted) return;

        try {
          const result = await checkProximity(
            loc.latitude,
            loc.longitude,
            destStop.lat,
            destStop.lng
          );

          if (!isMounted) return;
          setDistanceToDestination(Math.round(result.distance_meters));

          // Estimate which stop we're nearest (simple linear interpolation)
          const pct = 1 - result.distance_meters / 5000; // rough
          const estimatedIdx = Math.min(
            Math.max(Math.round(pct * totalStops), 0),
            totalStops
          );
          setCurrentStopIndex(estimatedIdx);

          // 1 stop before destination alert (within ~500m)
          if (
            result.distance_meters <= 500 &&
            result.distance_meters > 200 &&
            !alertedPenultimate
          ) {
            setAlertedPenultimate(true);
            Vibration.vibrate([0, 500, 200, 500]);
            setStatus("Next stop is your destination!");
            await speak(
              "Attention! Next stop is your destination. Prepare to get off."
            );
          }

          // Arrived alert (within 200m)
          if (result.alert && !alertedArrival) {
            setAlertedArrival(true);
            setArrived(true);
            Vibration.vibrate([0, 1000, 300, 1000]);
            setStatus(`Arrived at ${destStop.name}!`);
            await speak(
              `You have arrived at ${destStop.name}. Please exit the bus now.`
            );
          }
        } catch (err) {
          console.error("Proximity check error:", err);
        }
      }, 5000);

      subscriptionRef.current = sub;
    };

    init();

    return () => {
      isMounted = false;
      stopSpeaking();
      if (subscriptionRef.current) {
        subscriptionRef.current.remove();
      }
    };
  }, []);

  const handleEndRide = async () => {
    stopSpeaking();
    if (subscriptionRef.current) {
      subscriptionRef.current.remove();
    }
    await speak("Ride ended. Thank you for using PMPML Saarthi.");
    navigation.popToTop();
  };

  const handleRepeat = async () => {
    const remaining = totalStops - currentStopIndex;
    const msg = arrived
      ? `You have arrived at ${destStop.name}. Please exit now.`
      : `You are on ${routeData.route_name} heading to ${destStop.name}. ${remaining} stops remaining. ${
          distanceToDestination
            ? `You are approximately ${distanceToDestination} meters away.`
            : ""
        }`;
    await speak(msg);
  };

  const stopsRemaining = Math.max(totalStops - currentStopIndex, 0);

  return (
    <View style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor="#000" />

      {/* Header */}
      <Text
        style={styles.header}
        accessibilityRole="header"
        accessibilityLabel={`Active ride to ${destStop.name}`}
      >
        {arrived ? "🎉 Arrived!" : "🚌 Riding…"}
      </Text>

      {/* Status */}
      <Text style={styles.status} accessibilityLabel={status}>
        {status}
      </Text>

      {/* Route name */}
      <View style={styles.infoCard}>
        <Text style={styles.infoLabel}>Route</Text>
        <Text
          style={styles.infoValue}
          accessibilityLabel={`Route ${routeData.route_name}`}
        >
          {routeData.route_name}
        </Text>
      </View>

      {/* Destination */}
      <View style={styles.infoCard}>
        <Text style={styles.infoLabel}>Destination</Text>
        <Text
          style={styles.infoValue}
          accessibilityLabel={`Destination ${destStop.name}`}
        >
          {destStop.name}
        </Text>
      </View>

      {/* Stops remaining */}
      <View style={[styles.infoCard, styles.stopsCard]}>
        <Text style={styles.infoLabel}>Stops Remaining</Text>
        <Text
          style={styles.bigNumber}
          accessibilityLabel={`${stopsRemaining} stops remaining`}
        >
          {stopsRemaining}
        </Text>
      </View>

      {/* Distance */}
      {distanceToDestination !== null && (
        <View style={styles.infoCard}>
          <Text style={styles.infoLabel}>Distance</Text>
          <Text
            style={styles.infoValue}
            accessibilityLabel={`${distanceToDestination} meters to destination`}
          >
            {distanceToDestination >= 1000
              ? `${(distanceToDestination / 1000).toFixed(1)} km`
              : `${distanceToDestination} m`}
          </Text>
        </View>
      )}

      {/* Stop list progress */}
      <View style={styles.stopsProgress}>
        {stopsOnJourney.map((stopName, idx) => {
          const isPast = idx < currentStopIndex;
          const isCurrent = idx === currentStopIndex;
          const isDest = idx === stopsOnJourney.length - 1;
          return (
            <View key={idx} style={styles.stopRow}>
              <View
                style={[
                  styles.stopDot,
                  isPast && styles.stopDotPast,
                  isCurrent && styles.stopDotCurrent,
                  isDest && arrived && styles.stopDotArrived,
                ]}
              />
              <Text
                style={[
                  styles.stopName,
                  isPast && styles.stopNamePast,
                  isCurrent && styles.stopNameCurrent,
                ]}
                accessibilityLabel={`Stop ${idx + 1}: ${stopName}${
                  isCurrent ? " (current)" : ""
                }${isDest ? " (destination)" : ""}`}
              >
                {stopName}
                {isCurrent ? "  ← You" : ""}
                {isDest ? "  🏁" : ""}
              </Text>
            </View>
          );
        })}
      </View>

      {/* Action buttons */}
      <View style={styles.buttonRow}>
        <TouchableOpacity
          style={styles.repeatButton}
          onPress={handleRepeat}
          accessibilityLabel="Repeat current ride status"
          accessibilityRole="button"
        >
          <Text style={styles.buttonText}>🔁 Repeat</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.endButton}
          onPress={handleEndRide}
          accessibilityLabel="End ride and go back to home"
          accessibilityRole="button"
        >
          <Text style={styles.buttonText}>
            {arrived ? "✓ Done" : "✖ End Ride"}
          </Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#000",
    padding: 24,
  },
  header: {
    fontSize: 32,
    fontWeight: "bold",
    color: "#FFD600",
    textAlign: "center",
    marginBottom: 4,
    marginTop: 8,
  },
  status: {
    fontSize: 20,
    color: "#FFF",
    textAlign: "center",
    marginBottom: 20,
  },
  infoCard: {
    backgroundColor: "#1A1A1A",
    borderRadius: 12,
    padding: 16,
    marginBottom: 10,
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },
  stopsCard: {
    borderWidth: 2,
    borderColor: "#FFD600",
  },
  infoLabel: {
    fontSize: 16,
    color: "#888",
    fontWeight: "600",
    textTransform: "uppercase",
    letterSpacing: 1,
  },
  infoValue: {
    fontSize: 22,
    color: "#FFF",
    fontWeight: "bold",
  },
  bigNumber: {
    fontSize: 42,
    color: "#FFD600",
    fontWeight: "bold",
  },
  stopsProgress: {
    marginVertical: 16,
    paddingLeft: 8,
  },
  stopRow: {
    flexDirection: "row",
    alignItems: "center",
    marginBottom: 8,
  },
  stopDot: {
    width: 14,
    height: 14,
    borderRadius: 7,
    backgroundColor: "#333",
    marginRight: 12,
  },
  stopDotPast: {
    backgroundColor: "#666",
  },
  stopDotCurrent: {
    backgroundColor: "#FFD600",
    width: 18,
    height: 18,
    borderRadius: 9,
  },
  stopDotArrived: {
    backgroundColor: "#00E676",
  },
  stopName: {
    fontSize: 18,
    color: "#555",
  },
  stopNamePast: {
    color: "#777",
    textDecorationLine: "line-through",
  },
  stopNameCurrent: {
    color: "#FFD600",
    fontWeight: "bold",
    fontSize: 20,
  },
  buttonRow: {
    flexDirection: "row",
    gap: 12,
    marginTop: "auto",
    paddingBottom: 16,
  },
  repeatButton: {
    flex: 1,
    backgroundColor: "#333",
    borderRadius: 12,
    paddingVertical: 18,
    alignItems: "center",
    minHeight: 80,
    justifyContent: "center",
    borderWidth: 2,
    borderColor: "#FFD600",
  },
  endButton: {
    flex: 1,
    backgroundColor: "#FF3D00",
    borderRadius: 12,
    paddingVertical: 18,
    alignItems: "center",
    minHeight: 80,
    justifyContent: "center",
  },
  buttonText: {
    fontSize: 20,
    fontWeight: "700",
    color: "#FFF",
  },
});
