package com.genki.waveapidemo;

import androidx.activity.result.ActivityResultLauncher;
import androidx.activity.result.contract.ActivityResultContracts;
import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.ActivityCompat;
import androidx.core.content.PermissionChecker;

import android.Manifest;
import android.annotation.SuppressLint;
import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothDevice;
import android.bluetooth.BluetoothManager;
import android.bluetooth.le.BluetoothLeScanner;
import android.bluetooth.le.ScanCallback;
import android.bluetooth.le.ScanResult;
import android.content.Context;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;

import com.genki.wave.BatteryStatus;
import com.genki.wave.ButtonEvent;
import com.genki.wave.Datastream;
import com.genki.wave.WaveApiDevice;
import com.genki.wave.WaveApiListener;

import java.util.Arrays;
import java.util.Timer;
import java.util.TimerTask;

public class MainActivity extends AppCompatActivity implements WaveApiListener {
    private static final String TAG = "MainActivity";

    private BluetoothAdapter bluetoothAdapter;
    private BluetoothLeScanner leScanner;
    private WaveApiDevice wave;

    Datastream latestDatastream;
    BatteryStatus latestBatteryStatus;

    Timer batteryPollTimer;
    Timer updateTimer;

    static private final int BatteryUpdateRateHz = 1;
    static private final int SensorDataUpdateRateHz = 20;
    ActivityResultLauncher<Intent> activityResultLauncher = registerForActivityResult(
            new ActivityResultContracts.StartActivityForResult(),
            result -> {
            });

    private void updateViewVisibility(int visibility) {
        for (int id : Arrays.asList(R.id.waveDataLayout, R.id.buttonLayout))
            findViewById(id).setVisibility(visibility);
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);


        setContentView(R.layout.activity_main);

        updateViewVisibility(View.INVISIBLE);

        for (int buttonId : Arrays.asList(R.id.buttonA, R.id.buttonB, R.id.buttonC)) {
            findViewById(buttonId).setClickable(false);
        }

        ActivityCompat.requestPermissions(this,
                new String[]{
                        Manifest.permission.BLUETOOTH,
                        Manifest.permission.BLUETOOTH_ADMIN,
                        Manifest.permission.ACCESS_FINE_LOCATION,
                        Manifest.permission.ACCESS_COARSE_LOCATION,
                        Manifest.permission.BLUETOOTH_CONNECT
                },
                1);

        batteryPollTimer = new Timer();
        updateTimer = new Timer();

        updateTimer.scheduleAtFixedRate(new TimerTask() {
            @Override
            public void run() {
                runOnUiThread(new Runnable() {
                    @SuppressLint({"SetTextI18n", "DefaultLocale"})
                    public void run() {
                        if (latestDatastream != null) {
                            ((TextView) findViewById(R.id.gx)).setText(Float.toString(latestDatastream.data.gyro[0]));
                            ((TextView) findViewById(R.id.gy)).setText(Float.toString(latestDatastream.data.gyro[1]));
                            ((TextView) findViewById(R.id.gz)).setText(Float.toString(latestDatastream.data.gyro[2]));

                            ((TextView) findViewById(R.id.ax)).setText(Float.toString(latestDatastream.data.accel[0]));
                            ((TextView) findViewById(R.id.ay)).setText(Float.toString(latestDatastream.data.accel[1]));
                            ((TextView) findViewById(R.id.az)).setText(Float.toString(latestDatastream.data.accel[2]));

                            ((TextView) findViewById(R.id.qw)).setText(Float.toString(latestDatastream.motion.currentPose[0]));
                            ((TextView) findViewById(R.id.qx)).setText(Float.toString(latestDatastream.motion.currentPose[0]));
                            ((TextView) findViewById(R.id.qy)).setText(Float.toString(latestDatastream.motion.currentPose[1]));
                            ((TextView) findViewById(R.id.qz)).setText(Float.toString(latestDatastream.motion.currentPose[2]));
                        }

                        if (latestBatteryStatus != null) {
                            ((TextView) findViewById(R.id.batteryLabel)).setText(
                                    String.format("Battery: %d%%%s",
                                            (int) latestBatteryStatus.percentage,
                                            latestBatteryStatus.isCharging ? " (charging)" : ""));
                        }
                    }
                });
            }
        }, 0, 1000 / SensorDataUpdateRateHz);
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, @NonNull String[] permissions, @NonNull int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);

        for (int i = 0; i < permissions.length; ++i)
            Log.v(TAG, permissions[i] + ": " + (grantResults[i] == PermissionChecker.PERMISSION_GRANTED ? "Granted" : "Denied"));

        boolean hasBluetoothPermissions =
                ActivityCompat.checkSelfPermission(this, android.Manifest.permission.BLUETOOTH) == PackageManager.PERMISSION_GRANTED
                        && ActivityCompat.checkSelfPermission(this, android.Manifest.permission.BLUETOOTH_ADMIN) == PackageManager.PERMISSION_GRANTED;

        if (!hasBluetoothPermissions) {
            Log.e(TAG, "Need Bluetooth permissions to continue");
            return;
        }

        BluetoothManager manager = (BluetoothManager) getSystemService(Context.BLUETOOTH_SERVICE);
        bluetoothAdapter = manager.getAdapter();

        if (bluetoothAdapter == null) {
            Log.e(TAG, "Failed to get default Bluetooth adapter. Is Bluetooth supported?");
            return;
        }

        if (!bluetoothAdapter.isEnabled()) {
            Log.d(TAG, "Bluetooth is not enabled");

            Intent intent = new Intent(BluetoothAdapter.ACTION_REQUEST_ENABLE);
            activityResultLauncher.launch(intent);
        } else {
            startScan();
        }
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, @Nullable Intent data) {
        if (resultCode == RESULT_OK) {
            startScan();
        }

        super.onActivityResult(requestCode, resultCode, data);
    }

    @SuppressLint({"MissingPermission", "SetTextI18n"})
    private void startScan() {
        if (leScanner == null)
            leScanner = bluetoothAdapter.getBluetoothLeScanner();

        if (leScanner == null) {
            Log.e(TAG, "Failed to get Bluetooth LE scanner, is Bluetooth enabled?");
            return;
        }

        Log.i(TAG, "Starting LE scan...");

        TextView greeting = findViewById(R.id.greeting);
        greeting.setText("Scanning for devices...");

        leScanner.startScan(new ScanCallback() {
            private Context context;

            @SuppressLint("MissingPermission")
            public void onScanResult(int callbackType, ScanResult result) {
                BluetoothDevice device = result.getDevice();
                String name = device.getName();
                String address = device.getAddress();

                if (name != null && name.contains("Wave") && wave == null) {
                    Log.d(TAG, "Found Wave device: " + name + " (" + address + ")");

                    TextView greeting = findViewById(R.id.greeting);
                    greeting.setText("Connecting to " + name + " (" + address + ")");

                    wave = new WaveApiDevice(context, device, (WaveApiListener) context);
                }
            }

            private ScanCallback withContext(Context ctx) {
                this.context = ctx;
                return this;
            }
        }.withContext(this));
    }

    private void stopScan() {
        leScanner = null;
    }

    @SuppressLint({"MissingPermission", "SetTextI18n"})
    @Override
    public void onWaveConnected(BluetoothDevice device) {
        stopScan();

        TextView greeting = findViewById(R.id.greeting);
        greeting.setText("Connected to " + device.getName() + " (" + device.getAddress() + ")");

        updateViewVisibility(View.VISIBLE);

        batteryPollTimer.scheduleAtFixedRate(new TimerTask() {
            @Override
            public void run() {
                if (wave != null)
                    wave.requestBatteryStatus();
            }
        }, 0, 1000 / BatteryUpdateRateHz);
    }

    @Override
    public void onWaveDisconnected(BluetoothDevice device) {
        updateViewVisibility(View.INVISIBLE);

        batteryPollTimer.cancel();
        wave = null;
        startScan();
    }

    @Override
    public void onDatastream(Datastream ds) {
        latestDatastream = ds;
    }

    @Override
    public void onButtonEvent(ButtonEvent buttonEvent) {
        int id = buttonEvent.id == ButtonEvent.Id.A ? R.id.buttonA
                : buttonEvent.id == ButtonEvent.Id.B ? R.id.buttonB
                : buttonEvent.id == ButtonEvent.Id.C ? R.id.buttonC
                : 0;

        Button button = findViewById(id);

        if (buttonEvent.action == ButtonEvent.Action.Down) {
            button.performClick();
            button.setPressed(true);
            button.invalidate();
        } else if (Arrays.asList(ButtonEvent.Action.Up, ButtonEvent.Action.LongUp, ButtonEvent.Action.ExtraLongUp).contains(buttonEvent.action)) {
            button.setPressed(false);
            button.invalidate();
        }
    }

    @Override
    public void onBatteryStatus(BatteryStatus batteryStatus) {
        latestBatteryStatus = batteryStatus;
    }
}
