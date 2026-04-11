/**
 * HomeScreen.js — Landing screen with a large microphone button.
 *
 * On mount: TTS says "Welcome to PMPML Saarthi. Where would you like to go?"
 * User taps the mic, speaks a destination, and is navigated to RouteScreen.
 *
 * Accessibility: high-contrast black/yellow, 80x80 touch targets,
 * all elements have accessibilityLabel.
 */

import React, { useEffect, useState, useCallback } from "react";
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  StatusBar,
  Alert,
  TextInput,
  Platform,
  Vibration,
} from "react-native";
import { useFocusEffect } from "@react-navigation/native";
import { speak, startRecording, stopRecording, stopSpeaking } from "../services/voiceService";
import { parseDestination } from "../services/apiService";
import { getCurrentLocation } from "../services/locationService";

const GREETING = "Welcome to PMPML Saarthi. Where would you like to go?";

export default function HomeScreen({ navigation }) {
  const [listening, setListening] = useState(false);
  const [statusText, setStatusText] = useState("Tap the microphone and say your destination");
  const [manualText, setManualText] = useState("");

  // Speak greeting every time screen comes into focus
  useFocusEffect(
    useCallback(() => {
      const greet = async () => {
        setStatusText("Tap the microphone and say your destination");
        await speak(GREETING);
      };
      greet();
      return () => stopSpeaking();
    }, [])
  );

  const handleMicPress = async () => {
    if (listening) {
      // Stop recording
      setListening(false);
      Vibration.vibrate(100);
      setStatusText("Processing your request…");

      const uri = await stopRecording();

      if (uri) {
        // In a full app you'd POST the audio file to a Whisper STT endpoint.
        // For the MVP we fall back to a text prompt so the demo works on emulators.
        Alert.alert(
          "Voice Recorded",
          "Audio was saved. For this prototype, please type your destination below or say it now.",
          [{ text: "OK" }]
        );
        setStatusText('Type your destination below and press "Go"');
      }
      return;
    }

    // Start recording
    Vibration.vibrate(200);
    setListening(true);
    setStatusText("Listening… Tap again when done speaking");
    await speak("I am listening.");
    await startRecording();
  };

  const processDestination = async (text) => {
    if (!text || text.trim().length === 0) {
      await speak("I did not catch that. Please try again.");
      return;
    }

    setStatusText("Finding your route…");
    await speak("Looking up " + text);

    try {
      const result = await parseDestination(text);

      if (result.command === "cancel") {
        setStatusText("Cancelled. Tap the microphone to start again.");
        await speak("Cancelled.");
        return;
      }

      if (result.command === "repeat") {
        await speak(GREETING);
        return;
      }

      if (result.command === "where_am_i") {
        const loc = await getCurrentLocation();
        if (loc) {
          await speak(
            `Your current location is latitude ${loc.latitude.toFixed(4)}, longitude ${loc.longitude.toFixed(4)}.`
          );
        } else {
          await speak("I could not determine your location.");
        }
        return;
      }

      const destination = result.destination;
      if (!destination) {
        await speak("I could not understand the destination. Please try again.");
        setStatusText("Tap the microphone and say your destination");
        return;
      }

      // Get current location
      const loc = await getCurrentLocation();
      const userLat = loc?.latitude ?? 18.5156; // Fallback: Deccan Gymkhana
      const userLng = loc?.longitude ?? 73.8404;

      // Navigate to route screen
      navigation.navigate("Route", {
        destination,
        userLat,
        userLng,
      });
    } catch (err) {
      console.error("processDestination error:", err);
      await speak("Sorry, I could not reach the server. Please try again.");
      setStatusText("Server error. Tap the mic to retry.");
    }
  };

  return (
    <View style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor="#000" />

      {/* Title */}
      <Text
        style={styles.title}
        accessibilityLabel="PMPML Saarthi"
        accessibilityRole="header"
      >
        PMPML Saarthi
      </Text>

      <Text style={styles.subtitle} accessibilityLabel={statusText}>
        {statusText}
      </Text>

      {/* Large mic button */}
      <TouchableOpacity
        style={[styles.micButton, listening && styles.micButtonActive]}
        onPress={handleMicPress}
        accessibilityLabel={
          listening ? "Stop recording. Double tap to stop." : "Start recording. Double tap to speak your destination."
        }
        accessibilityRole="button"
        accessibilityHint="Press to speak your destination"
        activeOpacity={0.7}
      >
        <Text style={styles.micIcon}>{listening ? "⏹" : "🎤"}</Text>
        <Text style={styles.micLabel}>
          {listening ? "Tap to Stop" : "Tap to Speak"}
        </Text>
      </TouchableOpacity>

      {/* Manual text fallback (for emulators / demos) */}
      <View style={styles.manualInputContainer}>
        <Text style={styles.manualLabel} accessibilityLabel="Or type your destination">
          Or type your destination:
        </Text>
        <TextInput
          style={styles.textInput}
          placeholder="e.g. Shivajinagar"
          placeholderTextColor="#888"
          value={manualText}
          onChangeText={setManualText}
          accessibilityLabel="Destination text input"
          returnKeyType="go"
          onSubmitEditing={() => processDestination(manualText)}
        />
        <TouchableOpacity
          style={styles.goButton}
          onPress={() => processDestination(manualText)}
          accessibilityLabel="Go button. Press to search your typed destination."
          accessibilityRole="button"
        >
          <Text style={styles.goButtonText}>GO</Text>
        </TouchableOpacity>
      </View>

      {/* Voice command hints */}
      <View style={styles.hintsContainer}>
        <Text style={styles.hintTitle}>Voice commands:</Text>
        <Text style={styles.hintText}>• "Go to Shivajinagar"</Text>
        <Text style={styles.hintText}>• "Where am I"</Text>
        <Text style={styles.hintText}>• "Repeat"</Text>
        <Text style={styles.hintText}>• "Cancel"</Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#000",
    alignItems: "center",
    justifyContent: "center",
    paddingHorizontal: 24,
  },
  title: {
    fontSize: 36,
    fontWeight: "bold",
    color: "#FFD600",
    marginBottom: 8,
    textAlign: "center",
  },
  subtitle: {
    fontSize: 20,
    color: "#FFF",
    textAlign: "center",
    marginBottom: 32,
    lineHeight: 28,
  },
  micButton: {
    width: 160,
    height: 160,
    borderRadius: 80,
    backgroundColor: "#FFD600",
    justifyContent: "center",
    alignItems: "center",
    marginBottom: 32,
    elevation: 8,
    shadowColor: "#FFD600",
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.5,
    shadowRadius: 12,
  },
  micButtonActive: {
    backgroundColor: "#FF3D00",
    shadowColor: "#FF3D00",
  },
  micIcon: {
    fontSize: 56,
  },
  micLabel: {
    fontSize: 16,
    fontWeight: "700",
    color: "#000",
    marginTop: 4,
  },
  manualInputContainer: {
    width: "100%",
    maxWidth: 400,
    marginBottom: 24,
  },
  manualLabel: {
    color: "#FFD600",
    fontSize: 16,
    marginBottom: 8,
    fontWeight: "600",
  },
  textInput: {
    backgroundColor: "#1A1A1A",
    color: "#FFF",
    fontSize: 20,
    borderRadius: 12,
    paddingHorizontal: 16,
    paddingVertical: 14,
    borderWidth: 2,
    borderColor: "#FFD600",
    marginBottom: 12,
  },
  goButton: {
    backgroundColor: "#FFD600",
    borderRadius: 12,
    paddingVertical: 16,
    alignItems: "center",
    minHeight: 80,
    justifyContent: "center",
  },
  goButtonText: {
    fontSize: 24,
    fontWeight: "bold",
    color: "#000",
  },
  hintsContainer: {
    position: "absolute",
    bottom: 32,
    left: 24,
    right: 24,
  },
  hintTitle: {
    color: "#888",
    fontSize: 14,
    fontWeight: "700",
    marginBottom: 4,
  },
  hintText: {
    color: "#666",
    fontSize: 14,
    lineHeight: 20,
  },
});
