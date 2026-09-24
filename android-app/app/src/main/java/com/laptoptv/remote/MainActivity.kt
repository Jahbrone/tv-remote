package com.laptoptv.remote

import android.Manifest
import android.annotation.SuppressLint
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Build
import android.os.Bundle
import android.os.VibrationEffect
import android.os.Vibrator
import android.os.VibratorManager
import android.webkit.JavascriptInterface
import android.webkit.WebSettings
import android.webkit.WebView
import android.webkit.WebViewClient
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import java.net.InetSocketAddress
import java.net.Socket

class MainActivity : AppCompatActivity() {

    private lateinit var webView: WebView

    private val acerIp = "192.168.1.187"
    private val webPort = 8000

    private val remoteUrl =
        "http://$acerIp:$webPort"

    private val offlineUrl =
        "file:///android_asset/offline.html"

    companion object {
        private const val NOTIFICATION_PERMISSION_REQUEST = 100
    }


    // ----------------------------
    // HAPTIC BRIDGE
    // ----------------------------

    inner class HapticBridge {

        @JavascriptInterface
        fun click() {
            runOnUiThread {
                performClickHaptic()
            }
        }
    }


    // ----------------------------
    // OFFLINE REMOTE BRIDGE
    // ----------------------------

    inner class RemoteBridge {

        @JavascriptInterface
        fun retryConnection() {
            runOnUiThread {
                checkAcerAndLoad()
            }
        }
    }


    // ----------------------------
    // CREATE
    // ----------------------------

    @SuppressLint("SetJavaScriptEnabled")
    override fun onCreate(
        savedInstanceState: Bundle?
    ) {
        super.onCreate(savedInstanceState)

        setContentView(
            R.layout.activity_main
        )

        webView =
            findViewById(
                R.id.webView
            )


        webView.settings.apply {

            javaScriptEnabled =
                true

            domStorageEnabled =
                true

            cacheMode =
                WebSettings.LOAD_NO_CACHE

            allowFileAccess =
                true
        }


        webView.addJavascriptInterface(
            HapticBridge(),
            "AndroidHaptics"
        )


        webView.addJavascriptInterface(
            RemoteBridge(),
            "AndroidRemote"
        )


        webView.webViewClient =
            WebViewClient()


        // Always show the remote immediately.
        // If Acer is available, it will be replaced
        // with the live remote.
        showOfflineRemote()


        setupMediaControls()

        checkAcerAndLoad()
    }


    // ----------------------------
    // LOCK-SCREEN CONTROLS
    // ----------------------------

    private fun setupMediaControls() {

        if (
            Build.VERSION.SDK_INT >=
            Build.VERSION_CODES.TIRAMISU
        ) {

            if (
                ContextCompat.checkSelfPermission(
                    this,
                    Manifest.permission.POST_NOTIFICATIONS
                ) ==
                PackageManager.PERMISSION_GRANTED
            ) {

                startMediaControlService()

            } else {

                ActivityCompat.requestPermissions(
                    this,
                    arrayOf(
                        Manifest.permission.POST_NOTIFICATIONS
                    ),
                    NOTIFICATION_PERMISSION_REQUEST
                )
            }

        } else {

            startMediaControlService()
        }
    }


    override fun onRequestPermissionsResult(
        requestCode: Int,
        permissions: Array<out String>,
        grantResults: IntArray
    ) {

        super.onRequestPermissionsResult(
            requestCode,
            permissions,
            grantResults
        )


        if (
            requestCode ==
            NOTIFICATION_PERMISSION_REQUEST
        ) {

            if (
                grantResults.isNotEmpty() &&
                grantResults[0] ==
                PackageManager.PERMISSION_GRANTED
            ) {

                startMediaControlService()
            }
        }
    }


    private fun startMediaControlService() {

        val intent =
            Intent(
                this,
                MediaControlService::class.java
            ).apply {
                action =
                    MediaControlService.ACTION_REFRESH
            }

        ContextCompat.startForegroundService(
            this,
            intent
        )
    }


    // ----------------------------
    // HAPTIC FEEDBACK
    // ----------------------------

    private fun performClickHaptic() {

        val vibrator =
            if (
                Build.VERSION.SDK_INT >=
                Build.VERSION_CODES.S
            ) {

                val vibratorManager =
                    getSystemService(
                        Context.VIBRATOR_MANAGER_SERVICE
                    ) as VibratorManager

                vibratorManager.defaultVibrator

            } else {

                @Suppress("DEPRECATION")
                getSystemService(
                    Context.VIBRATOR_SERVICE
                ) as Vibrator
            }


        if (!vibrator.hasVibrator()) {
            return
        }


        if (
            Build.VERSION.SDK_INT >=
            Build.VERSION_CODES.O
        ) {

            vibrator.vibrate(
                VibrationEffect.createOneShot(
                    20,
                    VibrationEffect.DEFAULT_AMPLITUDE
                )
            )

        } else {

            @Suppress("DEPRECATION")
            vibrator.vibrate(
                20
            )
        }
    }


    // ----------------------------
    // ACER CONNECTION
    // ----------------------------

    private fun checkAcerAndLoad() {

        Thread {

            val online =
                try {

                    Socket().use { socket ->

                        socket.connect(
                            InetSocketAddress(
                                acerIp,
                                webPort
                            ),
                            2000
                        )
                    }

                    true

                } catch (
                    e: Exception
                ) {

                    false
                }


            runOnUiThread {

                if (online) {

                    webView.loadUrl(
                        remoteUrl
                    )

                } else {

                    showOfflineRemote()
                }
            }

        }.start()
    }


    // ----------------------------
    // OFFLINE REMOTE
    // ----------------------------

    private fun showOfflineRemote() {

        if (
            webView.url !=
            offlineUrl
        ) {

            webView.loadUrl(
                offlineUrl
            )
        }
    }
}