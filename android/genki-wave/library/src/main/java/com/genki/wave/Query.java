package com.genki.wave;

public class Query {
    public Query(byte type, byte id, short payloadSize) {
        this.type = type;
        this.id = id;
        this.payloadSize = payloadSize;
    }

    public static class Type {
        static final byte Request = 1;
        static final byte Response = 2;
        static final byte Stream = 3;
    }

    public static class Id {
        static final byte Datastream = 1;
        static final byte BatteryStatus = 2;
        static final byte DeviceInfo = 3;
        static final byte ButtonEvent = 4;
        static final byte DeviceMode = 5;
        static final byte Identify = 6;
        static final byte Recenter = 7;
        static final byte DisplayFrame = 8;
    }

    public byte type;
    public byte id;
    public short payloadSize;
}
