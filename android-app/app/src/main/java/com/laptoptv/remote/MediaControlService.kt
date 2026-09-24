package com.laptoptv.remote

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.app.Service
import android.content.Intent
import android.os.Build
import android.os.IBinder
import android.support.v4.media.session.MediaSessionCompat
import android.support.v4.media.session.PlaybackStateCompat
import androidx.core.app.NotificationCompat
import androidx.media.app.NotificationCompat.MediaStyle
import java.net.HttpURLConnection
import java.net.URL

class MediaControlService : Service() {

    companion object {
        private const val CHANNEL_ID =
            "kake_media_controls"

        private const val NOTIFICATION_ID =
            1001

        const val ACTION_VOLUME_DOWN =
            "com.laptoptv.remote.VOLUME_DOWN"

        const val ACTION_PLAY_PAUSE =
            "com.laptoptv.remote.PLAY_PAUSE"

        const val ACTION_VOLUME_UP =
            "com.laptoptv.remote.VOLUME_UP"

        const val ACTION_REFRESH =
            "com.laptoptv.remote.REFRESH_MEDIA"
    }

    private val acerIp = "192.168.1.187"
    private val serverPort = 8765

    private lateinit var mediaSession:
            MediaSessionCompat


    // ----------------------------
    // CREATE
    // ----------------------------

    override fun onCreate() {
        super.onCreate()

        createNotificationChannel()
        createMediaSession()

        startForeground(
            NOTIFICATION_ID,
            createNotification()
        )
    }


    // ----------------------------
    // MEDIA SESSION
    // ----------------------------

    private fun createMediaSession() {

        mediaSession =
            MediaSessionCompat(
                this,
                "KakeRuben"
            )

        mediaSession.setCallback(
            object :
                MediaSessionCompat.Callback() {

                override fun onPlay() {
                    sendCommand(
                        "play-pause"
                    )
                }

                override fun onPause() {
                    sendCommand(
                        "play-pause"
                    )
                }
            }
        )

        updatePlaybackState()

        mediaSession.isActive = true
    }


    private fun updatePlaybackState() {

        /*
         * Kake does not know the Acer's
         * actual playback state.
         *
         * We expose play/pause as a
         * simple toggle command.
         */

        val playbackState =
            PlaybackStateCompat.Builder()
                .setActions(
                    PlaybackStateCompat.ACTION_PLAY or
                            PlaybackStateCompat.ACTION_PAUSE or
                            PlaybackStateCompat.ACTION_PLAY_PAUSE
                )
                .setState(
                    PlaybackStateCompat.STATE_PLAYING,
                    PlaybackStateCompat.PLAYBACK_POSITION_UNKNOWN,
                    1f
                )
                .build()

        mediaSession.setPlaybackState(
            playbackState
        )
    }


    // ----------------------------
    // COMMAND HANDLING
    // ----------------------------

    override fun onStartCommand(
        intent: Intent?,
        flags: Int,
        startId: Int
    ): Int {

        when (intent?.action) {

            ACTION_VOLUME_DOWN -> {
                sendCommand(
                    "volume-down"
                )
            }

            ACTION_PLAY_PAUSE -> {
                sendCommand(
                    "play-pause"
                )
            }

            ACTION_VOLUME_UP -> {
                sendCommand(
                    "volume-up"
                )
            }

            ACTION_REFRESH -> {
                mediaSession.isActive = true
                updatePlaybackState()
                updateNotification()
            }
        }

        /*
         * Do not recreate the service
         * automatically after it is stopped.
         */
        return START_NOT_STICKY
    }


    // ----------------------------
    // NOTIFICATION CHANNEL
    // ----------------------------

    private fun createNotificationChannel() {

        if (
            Build.VERSION.SDK_INT >=
            Build.VERSION_CODES.O
        ) {

            val channel =
                NotificationChannel(
                    CHANNEL_ID,
                    "TV remote controls",
                    NotificationManager.IMPORTANCE_LOW
                )

            channel.description =
                "Kake Ruben TV controls"

            val manager =
                getSystemService(
                    NotificationManager::class.java
                )

            manager.createNotificationChannel(
                channel
            )
        }
    }


    // ----------------------------
    // NOTIFICATION
    // ----------------------------

    private fun createNotification():
            Notification {

        val openAppIntent =
            Intent(
                this,
                MainActivity::class.java
            )

        val openAppPendingIntent =
            PendingIntent.getActivity(
                this,
                0,
                openAppIntent,
                PendingIntent.FLAG_IMMUTABLE or
                        PendingIntent.FLAG_UPDATE_CURRENT
            )


        // ------------------------
        // VOLUME DOWN
        // ------------------------

        val volumeDownIntent =
            Intent(
                this,
                MediaControlService::class.java
            ).apply {
                action =
                    ACTION_VOLUME_DOWN
            }

        val volumeDownPendingIntent =
            PendingIntent.getService(
                this,
                1,
                volumeDownIntent,
                PendingIntent.FLAG_IMMUTABLE or
                        PendingIntent.FLAG_UPDATE_CURRENT
            )


        // ------------------------
        // PLAY / PAUSE
        // ------------------------

        val playPauseIntent =
            Intent(
                this,
                MediaControlService::class.java
            ).apply {
                action =
                    ACTION_PLAY_PAUSE
            }

        val playPausePendingIntent =
            PendingIntent.getService(
                this,
                2,
                playPauseIntent,
                PendingIntent.FLAG_IMMUTABLE or
                        PendingIntent.FLAG_UPDATE_CURRENT
            )


        // ------------------------
        // VOLUME UP
        // ------------------------

        val volumeUpIntent =
            Intent(
                this,
                MediaControlService::class.java
            ).apply {
                action =
                    ACTION_VOLUME_UP
            }

        val volumeUpPendingIntent =
            PendingIntent.getService(
                this,
                3,
                volumeUpIntent,
                PendingIntent.FLAG_IMMUTABLE or
                        PendingIntent.FLAG_UPDATE_CURRENT
            )


        // ------------------------
        // BASE NOTIFICATION
        // ------------------------

        val builder =
            NotificationCompat.Builder(
                this,
                CHANNEL_ID
            )
                .setSmallIcon(
                    R.mipmap.ic_launcher
                )
                .setContentTitle(
                    "Kake Ruben"
                )
                .setContentText(
                    "TV Remote"
                )
                .setContentIntent(
                    openAppPendingIntent
                )
                .setOngoing(true)
                .setOnlyAlertOnce(true)
                .setVisibility(
                    NotificationCompat.VISIBILITY_PUBLIC
                )
                .addAction(
                    R.drawable.ic_volume_down,
                    "Volume down",
                    volumeDownPendingIntent
                )
                .addAction(
                    R.drawable.ic_play_pause,
                    "Play / Pause",
                    playPausePendingIntent
                )
                .addAction(
                    R.drawable.ic_volume_up,
                    "Volume up",
                    volumeUpPendingIntent
                )


        // ------------------------
        // MODERN ANDROID
        // ------------------------
        //
        // Keep the existing MediaStyle
        // behaviour on Android 14+.
        //
        // This preserves the working
        // OnePlus 11 implementation.
        //

        if (
            Build.VERSION.SDK_INT >=
            Build.VERSION_CODES.UPSIDE_DOWN_CAKE
        ) {

            builder.setStyle(
                MediaStyle()
                    .setMediaSession(
                        mediaSession.sessionToken
                    )
                    .setShowActionsInCompactView(
                        0,
                        1,
                        2
                    )
            )
        }


        // ------------------------
        // ANDROID 13 AND BELOW
        // ------------------------
        //
        // Do NOT attach MediaStyle.
        //
        // OxygenOS 13 was replacing our
        // custom actions with its system
        // media player and only exposing
        // Play/Pause.
        //
        // Without MediaStyle, Android
        // renders our explicit notification
        // actions instead.
        //

        return builder.build()
    }


    private fun updateNotification() {

        val manager =
            getSystemService(
                NotificationManager::class.java
            )

        manager.notify(
            NOTIFICATION_ID,
            createNotification()
        )
    }


    // ----------------------------
    // ACER COMMAND
    // ----------------------------

    private fun sendCommand(
        command: String
    ) {

        Thread {

            var connection:
                    HttpURLConnection? = null

            try {

                val url =
                    URL(
                        "http://$acerIp:$serverPort/command"
                    )

                connection =
                    url.openConnection()
                            as HttpURLConnection

                connection.requestMethod =
                    "POST"

                connection.connectTimeout =
                    2000

                connection.readTimeout =
                    2000

                connection.doOutput =
                    true

                connection.setRequestProperty(
                    "Content-Type",
                    "application/json"
                )

                val body =
                    """
                    {"command":"$command"}
                    """.trimIndent()

                connection.outputStream.use {
                        output ->

                    output.write(
                        body.toByteArray(
                            Charsets.UTF_8
                        )
                    )
                }

                connection.responseCode

            } catch (_: Exception) {

                /*
                 * Acer unavailable.
                 * Nothing to do.
                 */

            } finally {

                connection?.disconnect()
            }
        }.start()
    }


    // ----------------------------
    // APP REMOVED FROM RECENTS
    // ----------------------------

    override fun onTaskRemoved(
        rootIntent: Intent?
    ) {

        stopMediaControls()

        super.onTaskRemoved(
            rootIntent
        )
    }


    // ----------------------------
    // CLEANUP
    // ----------------------------

    private fun stopMediaControls() {

        if (
            ::mediaSession.isInitialized
        ) {

            mediaSession.isActive =
                false

            mediaSession.release()
        }

        stopForeground(
            STOP_FOREGROUND_REMOVE
        )

        stopSelf()
    }


    override fun onDestroy() {

        if (
            ::mediaSession.isInitialized
        ) {

            mediaSession.isActive =
                false

            mediaSession.release()
        }

        stopForeground(
            STOP_FOREGROUND_REMOVE
        )

        super.onDestroy()
    }


    override fun onBind(
        intent: Intent?
    ): IBinder? {

        return null
    }
}