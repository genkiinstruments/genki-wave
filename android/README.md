# Wave by Genki Android library

Wave by Genki can be easily integrated into your Android app. For a higher level look at the API provided, please see the [documentation](https://www.notion.so/Wave-API-8a91bd3553ee4529878342dec477d93f).

## Dependencies

The project relies on [Android Studio](https://developer.android.com/studio).

Depending on your current Android Studio configuration, you might have to install the [Android NDK and CMake](https://developer.android.com/studio/projects/install-ndk) as well.

## Build

It's easiest to start with the examle app found in the [examples folder](examples/WaveApiDemo).

To integrate genki-wave into your app you need to take the following steps

1. In your app's root, locate `gradle.settings` and put the following 
```
include ':genki-wave'
project(':genki-wave').projectDir = new File('path/to/genki-wave/library')
```
2. In your app's `build.gradle` (not the top-level one), locate the dependencies section, and add
```
dependencies {
    ...
    implementation project(path: ':genki-wave')
}
```

## How to use the library

### Permissions

Make sure to declare the correct permissions in your `AppManifest.xml`

```xml
<uses-permission android:name="android.permission.BLUETOOTH_CONNECT" />
<uses-permission android:name="android.permission.BLUETOOTH_SCAN" /> <!-- Request legacy Bluetooth permissions on older devices. -->
<uses-permission android:name="android.permission.BLUETOOTH" android:maxSdkVersion="30" />
<uses-permission android:name="android.permission.BLUETOOTH_ADMIN" android:maxSdkVersion="30" />
```

Note that depending on your target SDK version, in addition to `BLUETOOTH_SCAN` you may also need

```xml
<uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION" />
<uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />
```

For more details on Bluetooth permissions, see the [Android developer website](https://developer.android.com/guide/topics/connectivity/bluetooth/permissions)

In your activity, you should start by requesting the required permissions

```java
ActivityCompat.requestPermissions(this,
                new String[]{
                        Manifest.permission.BLUETOOTH,
                        Manifest.permission.BLUETOOTH_ADMIN,
                        Manifest.permission.BLUETOOTH_SCAN,
                        Manifest.permission.ACCESS_FINE_LOCATION,
                        Manifest.permission.ACCESS_COARSE_LOCATION,
                        Manifest.permission.BLUETOOTH_CONNECT
                },
                BLUETOOTH_PERMISSIONS_REQUEST_CODE);
```

### Setting up Bluetooth

More details can be found on the [Android developer website](https://developer.android.com/guide/topics/connectivity/bluetooth/setup#java).

In your `onRequestPermissionsResult` callback, you can then grab a reference to the default Bluetooth adapter (assuming Bluetooth is enabled on the device - see the [Android developer website](https://developer.android.com/guide/topics/connectivity/bluetooth/setup#java) for how to prompt user to enable Bluetooth).

```java
this.bluetoothAdapter = ((BluetoothManager) getSystemService(Context.BLUETOOTH_SERVICE)).getAdapter();
```

### Scanning for devices

In order to discover Wave through Bluetooth, you need a reference to a `BluetoothLeScanner`

```java
this.leScanner = bluetoothAdapter.getBluetoothLeScanner();

...

this.leScanner.startScan(new ScanCallback() {
    private Context context;
    private WaveApiListener apiListener;


    public void onScanResult(int callbackType, ScanResult result) {
        BluetoothDevice device = result.getDevice();
        String name = device.getName();

        if (name != null && name.contains("Wave") && wave == null) {
            // "wave" instance variable grabbed from parent scope
            // Make sure to keep this reference somewhere while you want to retain the connection
            wave = new WaveApiDevice(context, device, apiListener);
        }
    }
    
    // Typically, the context and the listener refer to the same instance, but not required
    private ScanCallback withContext(Context ctx, WaveApiListener apiListener) {
        this.context = ctx;
        this.apiListener = apiListener;

        return this;
    }
}.withContext(this, this));


```

### The interface

Once connected, the interface for Wave is very simple. Implement `WaveApiListener` and you should receive callbacks when data is received from Wave.

For details on the packet payloads, please have a look at the data structures defined in the [com.genki.wave](genki-wave/library/src/main/java/com/genki/wave/) package.

```java
public interface WaveApiListener {
    void onWaveConnected(BluetoothDevice device);
    void onWaveDisconnected(BluetoothDevice device);

    void onDatastream(Datastream datastream);
    void onButtonEvent(ButtonEvent buttonEvent);
    void onBatteryStatus(BatteryStatus batteryStatus);
}
```

Wave accepts a number of commands that can be written back to the device. Currently, the Android library supports the following:

```java
public class WaveApiDevice {
    public void requestBatteryStatus(); // Request a battery level reading, will result in an WaveApiListener.onBatteryStatus callback.
    public void recenter(); // Request the internal pose (Datastream.motion.currentPose) to be reset to the origin.
}
```
