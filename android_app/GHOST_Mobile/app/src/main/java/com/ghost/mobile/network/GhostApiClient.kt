package com.ghost.mobile.network

import org.json.JSONObject
import java.io.OutputStreamWriter
import java.net.HttpURLConnection
import java.net.URL
import kotlin.concurrent.thread

object GhostApiClient {
    var serverHost: String = "192.168.1.100"
    var serverPort: Int = 8080
    var authToken: String = "ghost_alpha_clearance"

    private fun getBaseUrl(): String = "http://$serverHost:$serverPort"

    fun registerDevice(deviceId: String, name: String, ipAddress: String, battery: Int, callback: ((Boolean) -> Unit)? = null) {
        thread {
            try {
                val url = URL("${getBaseUrl()}/api/mobile/register")
                val conn = url.openConnection() as HttpURLConnection
                conn.requestMethod = "POST"
                conn.setRequestProperty("Content-Type", "application/json")
                conn.doOutput = true

                val payload = JSONObject().apply {
                    put("device_id", deviceId)
                    put("name", name)
                    put("ip_address", ipAddress)
                    put("battery_percent", battery)
                }

                OutputStreamWriter(conn.outputStream).use { it.write(payload.toString()) }
                val success = conn.responseCode in 200..299
                callback?.invoke(success)
            } catch (e: Exception) {
                callback?.invoke(false)
            }
        }
    }

    fun sendNotification(deviceId: String, appName: String, title: String, content: String, priority: String = "STANDARD") {
        thread {
            try {
                val url = URL("${getBaseUrl()}/api/mobile/notification")
                val conn = url.openConnection() as HttpURLConnection
                conn.requestMethod = "POST"
                conn.setRequestProperty("Content-Type", "application/json")
                conn.doOutput = true

                val payload = JSONObject().apply {
                    put("device_id", deviceId)
                    put("app_name", appName)
                    put("title", title)
                    put("content", content)
                    put("priority", priority)
                }

                OutputStreamWriter(conn.outputStream).use { it.write(payload.toString()) }
                conn.responseCode // execute
            } catch (e: Exception) {
                // Defensive logging
            }
        }
    }
}

