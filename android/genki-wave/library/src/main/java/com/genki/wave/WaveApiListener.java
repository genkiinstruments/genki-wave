package com.genki.wave;

import android.bluetooth.BluetoothDevice;

public interface WaveApiListener {
    void onWaveConnected(BluetoothDevice device);
    void onWaveDisconnected(BluetoothDevice device);

    void onDatastream(Datastream datastream);
    void onButtonEvent(ButtonEvent buttonEvent);
    void onBatteryStatus(BatteryStatus batteryStatus);
}
