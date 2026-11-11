# GHOST Mobile Companion (Android)

## Overview
The Android companion application bridges the physical operator's mobile device directly with the GHOST Central Command Center.

## Key Capabilities
1. **Notification Interception**:
   - Implements `NotificationListenerService` (`GhostNotificationService.kt`).
   - Receives all system and application push notifications.
   - Forwards parsed title, content, and application package to `POST /api/mobile/notification`.

2. **Device Telemetry**:
   - Monitors battery health, charging status, and WiFi connection details.
   - Pushes live updates to `POST /api/mobile/register` every 60 seconds.

3. **Remote Commands**:
   - Maintains an open WebSocket connection (`ws://<HOST>:8080/ws`) to receive real-time tactical alerts, voice notifications, and mission updates directly on the phone.

## Security Perimeter
- Communicates over local WiFi or encrypted tunnel.
- Uses `GHOST_GATEWAY_SECRET` token header for all mobile REST requests.

