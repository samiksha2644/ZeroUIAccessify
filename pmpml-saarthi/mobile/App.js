/**
 * App.js — Root navigator for PMPML Saarthi.
 *
 * Uses React Navigation's stack navigator with three screens:
 *   Home → Route → Ride
 *
 * The navigation bar is hidden as TTS handles all transitions.
 */

import React from "react";
import { NavigationContainer } from "@react-navigation/native";
import { createNativeStackNavigator } from "@react-navigation/native-stack";

import HomeScreen from "./screens/HomeScreen";
import RouteScreen from "./screens/RouteScreen";
import RideScreen from "./screens/RideScreen";

const Stack = createNativeStackNavigator();

export default function App() {
  return (
    <NavigationContainer>
      <Stack.Navigator
        initialRouteName="Home"
        screenOptions={{
          headerStyle: { backgroundColor: "#000" },
          headerTintColor: "#FFD600",
          headerTitleStyle: { fontWeight: "bold", fontSize: 20 },
          animation: "slide_from_right",
        }}
      >
        <Stack.Screen
          name="Home"
          component={HomeScreen}
          options={{ headerShown: false }}
        />
        <Stack.Screen
          name="Route"
          component={RouteScreen}
          options={{
            title: "Route Details",
            headerBackAccessibilityLabel: "Go back to home",
          }}
        />
        <Stack.Screen
          name="Ride"
          component={RideScreen}
          options={{
            title: "Active Ride",
            headerBackVisible: false, // prevent accidental back during ride
          }}
        />
      </Stack.Navigator>
    </NavigationContainer>
  );
}
