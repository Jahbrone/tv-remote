package com.laptoptv.remote

import android.annotation.SuppressLint
import android.os.Bundle
import android.view.View
import android.webkit.WebSettings
import android.webkit.WebView
import android.webkit.WebViewClient
import android.widget.Button
import android.widget.LinearLayout
import androidx.appcompat.app.AppCompatActivity
import java.net.InetSocketAddress
import java.net.Socket

class MainActivity : AppCompatActivity() {

    private lateinit var webView: WebView
    private lateinit var loadingView: LinearLayout
    private lateinit var offlineView: LinearLayout

    private val acerIp = "192.168.1.187"
    private val webPort = 8000
    private val remoteUrl = "http://$acerIp:$webPort"

    @SuppressLint("SetJavaScriptEnabled")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        webView = findViewById(R.id.webView)
        loadingView = findViewById(R.id.loadingView)
        offlineView = findViewById(R.id.offlineView)

        val retryButton = findViewById<Button>(R.id.retryButton)

        webView.settings.apply {
            javaScriptEnabled = true
            domStorageEnabled = true
            cacheMode = WebSettings.LOAD_NO_CACHE
        }

        webView.webViewClient = WebViewClient()

        retryButton.setOnClickListener {
            checkAcerAndLoad()
        }

        checkAcerAndLoad()
    }

    private fun checkAcerAndLoad() {
        showLoading()

        Thread {
            val online = try {
                Socket().use { socket ->
                    socket.connect(
                        InetSocketAddress(acerIp, webPort),
                        2000
                    )
                }
                true
            } catch (e: Exception) {
                false
            }

            runOnUiThread {
                if (online) {
                    showWebView()
                    webView.clearCache(true)
                    webView.loadUrl(remoteUrl)
                } else {
                    showOffline()
                }
            }
        }.start()
    }

    private fun showLoading() {
        webView.visibility = View.GONE
        offlineView.visibility = View.GONE
        loadingView.visibility = View.VISIBLE
    }

    private fun showOffline() {
        webView.visibility = View.GONE
        loadingView.visibility = View.GONE
        offlineView.visibility = View.VISIBLE
    }

    private fun showWebView() {
        loadingView.visibility = View.GONE
        offlineView.visibility = View.GONE
        webView.visibility = View.VISIBLE
    }
}