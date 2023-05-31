package com.genki.wave;


import android.util.Log;

import java.nio.ByteBuffer;
import java.nio.ByteOrder;

public class ButtonEvent {
    public static class Action {
        public static final byte Up = 0;
        public static final byte Down = 1;
        public static final byte Long = 2;
        public static final byte LongUp = 3;
        public static final byte ExtraLong = 4;
        public static final byte ExtraLongUp = 5;
        public static final byte Click = 6;
        public static final byte DoubleClick = 7;
    }

    public static class Id {
        public static final byte A = 0;
        public static final byte B = 1;
        public static final byte C = 2;
    }

    public byte id;
    public byte action;
    public float timestamp;

    public static ButtonEvent FromBytes(byte[] bytes) {
        ButtonEvent be = new ButtonEvent();
        ByteBuffer bb = ByteBuffer.wrap(bytes).order(ByteOrder.LITTLE_ENDIAN);

        be.id = bb.get();
        be.action = bb.get();
        bb.position(4);
        be.timestamp = bb.getFloat();

        return be;
    }
}
