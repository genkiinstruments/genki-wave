package com.genki.wave;

import android.util.Log;

public class PacketHandler {
    public interface Writer {
        void transmitPacket(byte[] packet);
    }

    // Used to load the 'wave' native library on application startup.
    static {
        System.loadLibrary("genkiwave");
    }

    private static final String TAG = "PacketHandler";

    public long nativeHandle;
    WaveApiListener listener;
    Writer writer;

    public PacketHandler(long mtu, WaveApiListener apiListener, Writer writer) {
        Log.d(TAG, "Using MTU: " + mtu);
        nativeHandle = ConstructNative(mtu);
        this.listener = apiListener;
        this.writer = writer;
    }

    @Override
    protected void finalize() {
        CleanupNative(nativeHandle);
    }

    public void push(byte[] bytes) {
        PushBytesNative(nativeHandle, bytes);
    }

    public boolean sendQuery(Query query) {
        return SendQueryNative(nativeHandle, query, new byte[0]);
    }

    public boolean sendQuery(Query query, byte[] payload) {
        return SendQueryNative(nativeHandle, query, payload);
    }

    public void onWriteComplete(boolean success) {
        OnWriteCompleteNative(nativeHandle, success);
    }

    private void writePacket(byte[] payload) {
        writer.transmitPacket(payload); }

    native long ConstructNative(long mtu);

    native void CleanupNative(long handle);

    native void PushBytesNative(long handle, byte[] bytes);

    native boolean SendQueryNative(long handle, Query query, byte[] payload);

    native void OnWriteCompleteNative(long handle, boolean success);

    void handleQuery(int id, byte[] payload) {
        switch (id) {
            case Query.Id.Datastream:
                listener.onDatastream(Datastream.FromBytes(payload));
                break;

            case Query.Id.ButtonEvent:
                listener.onButtonEvent(ButtonEvent.FromBytes(payload));
                break;

            case Query.Id.BatteryStatus:
                listener.onBatteryStatus(BatteryStatus.FromBytes(payload));
                break;

            default:
                break;
        }
    }
}
