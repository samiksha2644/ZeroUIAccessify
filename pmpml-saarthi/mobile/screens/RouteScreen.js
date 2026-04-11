/**
 * RouteScreen.js — Displays route info as large, high-contrast cards.
 *
 * Receives { destination, userLat, userLng } via route params.
 * Calls /find-route on mount, speaks the result, then lets the user
 * start their ride (navigates to RideScreen).
 */

import React, { useEffect, useState } from "react";
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  ScrollView,
  ActivityIndicator,
  StatusBar,
} from "react-native";
import { speak, stopSpeaking } from "../services/voiceService";
import { findRoute } from "../services/apiService";

export default function RouteScreen({ route, navigation }) {
  const { destination, userLat, userLng } = route.params;
  const [routeData, setRouteData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;

    const fetchRoute = async () => {
      try {
        await speak(`Searching for a route to ${destination}.`);
        const data = await findRoute(userLat, userLng, destination);
        if (cancelled) return;
        setRouteData(data);
        setLoading(false);
        await speak(data.speech);
      } catch (err) {
        console.error("RouteScreen fetchRoute error:", err);
        if (cancelled) return;
        setError("Could not find a route. Please go back and try again.");
        setLoading(false);
        await speak("Sorry, I could not find a route. Please go back and try again.");
      }
    };

    fetchRoute();
    return () => {
      cancelled = true;
      stopSpeaking();
    };
  }, [destination, userLat, userLng]);

  const handleRepeat = async () => {
    if (routeData) {
      await speak(routeData.speech);
    }
  };

  const handleStartRide = () => {
    if (!routeData) return;
    navigation.navigate("Ride", {
      routeData,
    });
  };

  const handleGoBack = async () => {
    stopSpeaking();
    navigation.goBack();
  };

  if (loading) {
    return (
      <View style={styles.container}>
        <StatusBar barStyle="light-content" backgroundColor="#000" />
        <ActivityIndicator size="large" color="#FFD600" />
        <Text style={styles.loadingText} accessibilityLabel="Loading route information">
          Finding your route…
        </Text>
      </View>
    );
  }

  if (error) {
    return (
      <View style={styles.container}>
        <StatusBar barStyle="light-content" backgroundColor="#000" />
        <Text style={styles.errorText} accessibilityLabel={error}>
          {error}
        </Text>
        <TouchableOpacity
          style={styles.actionButton}
          onPress={handleGoBack}
          accessibilityLabel="Go back to home screen"
          accessibilityRole="button"
        >
          <Text style={styles.actionButtonText}>← Go Back</Text>
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <ScrollView
      style={styles.scrollContainer}
      contentContainerStyle={styles.scrollContent}
    >
      <StatusBar barStyle="light-content" backgroundColor="#000" />

      {/* Header */}
      <Text style={styles.header} accessibilityRole="header">
        Your Route
      </Text>

      {/* Walk card */}
      <View
        style={styles.card}
        accessible={true}
        accessibilityLabel={`Walk ${Math.round(routeData.walk_distance_meters)} meters ${routeData.walk_direction} to ${routeData.nearest_stop.name} bus stop`}
      >
        <Text style={styles.cardEmoji}>🚶</Text>
        <Text style={styles.cardTitle}>Walk to Stop</Text>
        <Text style={styles.cardBody}>
          {Math.round(routeData.walk_distance_meters)}m {routeData.walk_direction} to{" "}
          <Text style={styles.highlight}>{routeData.nearest_stop.name}</Text>
        </Text>
      </View>

      {/* Bus card */}
      <View
        style={styles.card}
        accessible={true}
        accessibilityLabel={`Board ${routeData.route_name} arriving in ${routeData.next_bus_eta_minutes} minutes`}
      >
        <Text style={styles.cardEmoji}>🚌</Text>
        <Text style={styles.cardTitle}>Board Bus</Text>
        <Text style={styles.cardBody}>
          <Text style={styles.highlight}>{routeData.route_name}</Text> — arriving in{" "}
          <Text style={styles.highlight}>{routeData.next_bus_eta_minutes} min</Text>
        </Text>
      </View>

      {/* Journey card */}
      <View
        style={styles.card}
        accessible={true}
        accessibilityLabel={`Journey has ${routeData.total_stops} stops from ${routeData.nearest_stop.name} to ${routeData.destination_stop.name}`}
      >
        <Text style={styles.cardEmoji}>📍</Text>
        <Text style={styles.cardTitle}>Journey</Text>
        <Text style={styles.cardBody}>
          {routeData.total_stops} stops:{" "}
          {routeData.stops_on_journey.join(" → ")}
        </Text>
      </View>

      {/* Destination card */}
      <View
        style={[styles.card, styles.cardDestination]}
        accessible={true}
        accessibilityLabel={`Destination: ${routeData.destination_stop.name}`}
      >
        <Text style={styles.cardEmoji}>🏁</Text>
        <Text style={styles.cardTitle}>Destination</Text>
        <Text style={styles.cardBody}>
          <Text style={styles.highlight}>{routeData.destination_stop.name}</Text>
        </Text>
      </View>

      {/* Action buttons */}
      <View style={styles.buttonRow}>
        <TouchableOpacity
          style={[styles.actionButton, styles.repeatButton]}
          onPress={handleRepeat}
          accessibilityLabel="Repeat route information"
          accessibilityRole="button"
        >
          <Text style={styles.actionButtonText}>🔁 Repeat</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.actionButton, styles.cancelButton]}
          onPress={handleGoBack}
          accessibilityLabel="Cancel and go back"
          accessibilityRole="button"
        >
          <Text style={styles.actionButtonText}>✖ Cancel</Text>
        </TouchableOpacity>
      </View>

      <TouchableOpacity
        style={styles.startRideButton}
        onPress={handleStartRide}
        accessibilityLabel="Start ride. Press when you have boarded the bus."
        accessibilityRole="button"
      >
        <Text style={styles.startRideText}>🚌  Start Ride</Text>
      </TouchableOpacity>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#000",
    justifyContent: "center",
    alignItems: "center",
    padding: 24,
  },
  scrollContainer: {
    flex: 1,
    backgroundColor: "#000",
  },
  scrollContent: {
    padding: 24,
    paddingBottom: 48,
  },
  loadingText: {
    color: "#FFD600",
    fontSize: 22,
    marginTop: 20,
    textAlign: "center",
  },
  errorText: {
    color: "#FF3D00",
    fontSize: 22,
    textAlign: "center",
    marginBottom: 24,
  },
  header: {
    fontSize: 32,
    fontWeight: "bold",
    color: "#FFD600",
    textAlign: "center",
    marginBottom: 24,
  },
  card: {
    backgroundColor: "#1A1A1A",
    borderRadius: 16,
    padding: 20,
    marginBottom: 16,
    borderLeftWidth: 5,
    borderLeftColor: "#FFD600",
  },
  cardDestination: {
    borderLeftColor: "#00E676",
  },
  cardEmoji: {
    fontSize: 32,
    marginBottom: 4,
  },
  cardTitle: {
    fontSize: 18,
    fontWeight: "700",
    color: "#FFD600",
    marginBottom: 6,
    textTransform: "uppercase",
    letterSpacing: 1,
  },
  cardBody: {
    fontSize: 22,
    color: "#FFF",
    lineHeight: 30,
  },
  highlight: {
    color: "#FFD600",
    fontWeight: "bold",
  },
  buttonRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    marginTop: 8,
    marginBottom: 16,
    gap: 12,
  },
  actionButton: {
    flex: 1,
    backgroundColor: "#333",
    borderRadius: 12,
    paddingVertical: 18,
    alignItems: "center",
    minHeight: 80,
    justifyContent: "center",
  },
  repeatButton: {
    borderWidth: 2,
    borderColor: "#FFD600",
  },
  cancelButton: {
    borderWidth: 2,
    borderColor: "#FF3D00",
  },
  actionButtonText: {
    fontSize: 20,
    fontWeight: "700",
    color: "#FFF",
  },
  startRideButton: {
    backgroundColor: "#00E676",
    borderRadius: 16,
    paddingVertical: 22,
    alignItems: "center",
    minHeight: 80,
    justifyContent: "center",
    elevation: 6,
    shadowColor: "#00E676",
    shadowOffset: { width: 0, height: 3 },
    shadowOpacity: 0.4,
    shadowRadius: 8,
  },
  startRideText: {
    fontSize: 26,
    fontWeight: "bold",
    color: "#000",
  },
});
