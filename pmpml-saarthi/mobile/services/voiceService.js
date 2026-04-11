/**
 * voiceService.js — Text-to-Speech and Speech-to-Text wrapper
 *
 * TTS  → expo-speech
 * STT  → expo-av (records audio; the backend or a future STT service transcribes)
 *
 * For the MVP we simulate STT by recording audio and returning a placeholder.
 * In production you would POST the recording to a Whisper endpoint.
 */

import * as Speech from "expo-speech";
import { Audio } from "expo-av";

let recording = null;

/**
 * Speak text aloud. Returns a promise that resolves when speech finishes.
 */
export function speak(text, options = {}) {
  return new Promise((resolve, reject) => {
    Speech.speak(text, {
      language: "en-IN",
      rate: 0.9,
      pitch: 1.0,
      ...options,
      onDone: resolve,
      onError: reject,
      onStopped: resolve,
    });
  });
}

/**
 * Stop any speech currently playing.
 */
export function stopSpeaking() {
  Speech.stop();
}

/**
 * Begin recording audio from the microphone.
 * Must call stopRecording() later to get the URI.
 */
export async function startRecording() {
  try {
    const permission = await Audio.requestPermissionsAsync();
    if (!permission.granted) {
      throw new Error("Microphone permission not granted");
    }

    await Audio.setAudioModeAsync({
      allowsRecordingIOS: true,
      playsInSilentModeIOS: true,
    });

    const { recording: rec } = await Audio.Recording.createAsync(
      Audio.RecordingOptionsPresets.HIGH_QUALITY
    );
    recording = rec;
    return true;
  } catch (err) {
    console.error("startRecording error:", err);
    return false;
  }
}

/**
 * Stop recording and return the local file URI.
 */
export async function stopRecording() {
  if (!recording) return null;
  try {
    await recording.stopAndUnloadAsync();
    const uri = recording.getURI();
    recording = null;
    return uri;
  } catch (err) {
    console.error("stopRecording error:", err);
    recording = null;
    return null;
  }
}

/**
 * Check if we're currently recording.
 */
export function isRecording() {
  return recording !== null;
}
