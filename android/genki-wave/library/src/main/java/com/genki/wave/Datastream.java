package com.genki.wave;


import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.nio.FloatBuffer;

public class Datastream {
    public static class SensorData {
        public float[] gyro = new float[3];
        public float[] accel = new float[3];
        public float[] mag = new float[3];
    }

    public SensorData data = new SensorData();

    public static class MotionData {
        public float[] rawPose = new float[4];
        public float[] currentPose = new float[4];
        public float[] euler = new float[3];
        public float[] linearAccel = new float[3];

        static class Peak {
            public boolean detected;
            public float normVelocity;
        }

        public Peak peak = new Peak();
    }

    public MotionData motion = new MotionData();
    public long timestampUs = 0;

    static float[] GetFloatArray(ByteBuffer bytes, int numBytes) {
        byte[] float3d = new byte[numBytes];
        bytes.get(float3d, 0, float3d.length);

        FloatBuffer fbuf = ByteBuffer.wrap(float3d).order(ByteOrder.LITTLE_ENDIAN).asFloatBuffer();
        float[] floats = new float[numBytes / 4];
        fbuf.get(floats);

        return floats.clone();
    }

    public static Datastream FromBytes(byte[] bytes) {
        Datastream ds = new Datastream();

        ByteBuffer bb = ByteBuffer.wrap(bytes).order(ByteOrder.LITTLE_ENDIAN);

        ds.data.gyro = GetFloatArray(bb, 12);
        ds.data.accel = GetFloatArray(bb, 12);
        ds.data.mag = GetFloatArray(bb, 12);

        ds.motion.rawPose = GetFloatArray(bb, 16);
        ds.motion.currentPose = GetFloatArray(bb, 16);
        ds.motion.euler = GetFloatArray(bb, 12);
        ds.motion.linearAccel = GetFloatArray(bb, 12);

        ds.motion.peak.detected = bb.get() > 0;
        ds.motion.peak.normVelocity = bb.getFloat();

        ds.timestampUs = bb.getLong();

        return ds;
    }
}
