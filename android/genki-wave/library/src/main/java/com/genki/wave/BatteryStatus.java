package com.genki.wave;

import java.nio.ByteBuffer;
import java.nio.ByteOrder;

public class BatteryStatus {
    public float voltage;
    public float percentage;
    public boolean isCharging;

    public static BatteryStatus FromBytes(byte[] bytes) {
        BatteryStatus bs = new BatteryStatus();
        ByteBuffer bb = ByteBuffer.wrap(bytes).order(ByteOrder.LITTLE_ENDIAN);

        bs.voltage = bb.getFloat();
        bs.percentage = bb.getFloat();
        bs.isCharging = bb.get() > 0;

        return bs;
    }
}
