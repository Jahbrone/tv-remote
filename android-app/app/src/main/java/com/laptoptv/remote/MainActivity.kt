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
import android.view.View
import android.webkit.JavascriptInterface
import android.webkit.WebSettings
import android.webkit.WebView
import android.webkit.WebViewClient
import android.widget.Button
import android.widget.LinearLayout
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import java.net.InetSocketAddress
import java.net.Socket

class MainActivity : AppCompatActivity() {

    private lateinit var webView: WebView
    private lateinit var loadingView: LinearLayout
    private lateinit var offlineView: LinearLayout

    private val acerIp = "192.168.1.187"
    private val webPort = 8000
    private val remoteUrl = "http://$acerIp:$webPort"

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
    // CREATE
    // ----------------------------

    @SuppressLint("SetJavaScriptEnabled")
    override fun onCreate(
        savedInstanceState: Bundle?
    ) {
        super.onCreate(
            savedInstanceState
        )

        setContentView(
            R.layout.activity_main
        )


        webView =
            findViewById(
                R.id.webView
            )

        loadingView =
            findViewById(
                R.id.loadingView
            )

        offlineView =
            findViewById(
                R.id.offlineView
            )


        val retryButton =
            findViewById<Button>(
                R.id.retryButton
            )


        webView.settings.apply {

            javaScriptEnabled =
                true

            domStorageEnabled =
                true

            cacheMode =
                WebSettings.LOAD_NO_CACHE
        }


        webView.addJavascriptInterface(
            HapticBridge(),
            "AndroidHaptics"
        )


        webView.webViewClient =
            WebViewClient()


        retryButton.setOnClickListener {

            checkAcerAndLoad()
        }


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
            )


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


        if (
            !vibrator.hasVibrator()
        ) {
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

        showLoading()


        Thread {

            val online =
                try {

                    Socket().use {
                            socket ->

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

                    showWebView()

                    webView.clearCache(
                        true
                    )

                    webView.loadUrl(
                        remoteUrl
                    )

                } else {

                    showOffline()
                }
            }

        }.start()
    }


    // ----------------------------
    // UI STATES
    // ----------------------------

    private fun showLoading() {

        webView.visibility =
            View.GONE

        offlineView.visibility =
            View.GONE

        loadingView.visibility =
            View.VISIBLE
    }


    private fun showOffline() {

        webView.visibility =
            View.GONE

        loadingView.visibility =
            View.GONE

        offlineView.visibility =
            View.VISIBLE
    }


    private fun showWebView() {

        loadingView.visibility =
            View.GONE

        offlineView.visibility =
            View.GONE

        webView.visibility =
            View.VISIBLE
    }
}