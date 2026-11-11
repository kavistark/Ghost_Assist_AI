package com.ghost.mobile.services

import android.app.Service
import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import android.os.BatteryManager
import android.os.IBinder
import com.ghost.mobile.network.GhostApiClient
import java.util.Timer
import java.util.TimerTask

class GhostSyncService : Service() {

    private var syncTimer: Timer? = null

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        startTelemetryLoop()
        return START_STICKY
    }

    private fun startTelemetryLoop() {
        syncTimer?.cancel()
        syncTimer = Timer()
        syncTimer?.scheduleAtFixedRate(object : TimerTask() {
            override fun run() {
                val battery = getBatteryPercentage()
                GhostApiClient.registerDevice(
                    deviceId = "ANDROID-NODE-01",
                    name = "Operator Android Handset",
                    ipAddress = "192.168.1.150",
                    battery = battery
                )
            }
        }, 0, 60000) // every 60s
    }

    private fun getBatteryPercentage(): Int {
        val ifilter = IntentFilter(Intent.ACTION_BATTERY_CHANGED)
        val batteryStatus: Intent? = registerReceiver(null, ifilter)
        val level = batteryStatus?.getIntExtra(BatteryManager.EXTRA_LEVEL, -1) ?: -1
        val scale = batteryStatus?.getIntExtra(BatteryManager.EXTRA_SCALE, -1) ?: -1
        return if (level >= 0 && scale > 0) (level * 100 / scale) else 100
    }

    override fun onDestroy() {
        syncTimer?.cancel()
        super.onDestroy()
    }

    override fun onBind(intent: Intent?): IBinder? = null
}

