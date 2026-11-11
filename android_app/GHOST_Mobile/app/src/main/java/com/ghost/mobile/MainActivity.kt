package com.ghost.mobile

import android.app.Activity
import android.content.Intent
import android.os.Bundle
import android.provider.Settings
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import android.widget.Toast
import com.ghost.mobile.network.GhostApiClient
import com.ghost.mobile.services.GhostSyncService

class MainActivity : Activity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Programmatic tactical layout
        val layout = android.widget.LinearLayout(this).apply {
            orientation = android.widget.LinearLayout.VERTICAL
            setBackgroundColor(0xFF06090E.toInt())
            setPadding(48, 64, 48, 64)
        }

        val title = TextView(this).apply {
            text = "GHOST // MOBILE COMPANION"
            setTextColor(0xFF00FF88.toInt())
            textSize = 20f
            typeface = android.graphics.Typeface.MONOSPACE
        }

        val subtitle = TextView(this).apply {
            text = "TACTICAL NODE 02 — DEFCON 3"
            setTextColor(0xFF00E5FF.toInt())
            textSize = 12f
            setPadding(0, 8, 0, 48)
            typeface = android.graphics.Typeface.MONOSPACE
        }

        val ipInput = EditText(this).apply {
            hint = "Command Center IP (e.g. 192.168.1.100)"
            setTextColor(0xFFFFFFFF.toInt())
            setHintTextColor(0xFF607D94.toInt())
            setText(GhostApiClient.serverHost)
        }

        val connectBtn = Button(this).apply {
            text = "ESTABLISH SECURE LINK"
            setBackgroundColor(0xFF1A2A3A.toInt())
            setTextColor(0xFF00FF88.toInt())
            setOnClickListener {
                GhostApiClient.serverHost = ipInput.text.toString().trim()
                startService(Intent(this@MainActivity, GhostSyncService::class.java))
                Toast.makeText(this@MainActivity, "GHOST Sync Link Armed", Toast.LENGTH_SHORT).show()
            }
        }

        val notifBtn = Button(this).apply {
            text = "GRANT NOTIFICATION ACCESS"
            setBackgroundColor(0xFF121B24.toInt())
            setTextColor(0xFF00E5FF.toInt())
            setOnClickListener {
                startActivity(Intent(Settings.ACTION_NOTIFICATION_LISTENER_SETTINGS))
            }
        }

        layout.addView(title)
        layout.addView(subtitle)
        layout.addView(ipInput)
        layout.addView(connectBtn)
        layout.addView(notifBtn)

        setContentView(layout)
    }
}

