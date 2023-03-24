package com.genki.wave;

import android.annotation.SuppressLint;
import android.bluetooth.BluetoothDevice;
import android.bluetooth.BluetoothGatt;
import android.bluetooth.BluetoothGattCharacteristic;
import android.bluetooth.BluetoothGattDescriptor;
import android.bluetooth.BluetoothGattService;
import android.content.Context;
import android.util.Log;

import androidx.annotation.NonNull;

import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import java.util.UUID;
import java.util.stream.Collectors;

import no.nordicsemi.android.ble.BleManager;
import no.nordicsemi.android.ble.SimpleRequest;
import no.nordicsemi.android.ble.callback.FailCallback;
import no.nordicsemi.android.ble.callback.SuccessCallback;

public class WaveApiDevice {
    private static final String TAG = "genki-wave";
    private static final int MTU_TO_REQUEST = 247;

    private final ConnectionManager manager;

    @SuppressLint("MissingPermission")
    public WaveApiDevice(@NonNull Context context, BluetoothDevice device, WaveApiListener apiListener) {
        this.manager = new ConnectionManager(context, apiListener);

        manager.connect(device)
                .retry(3, 100)
                .useAutoConnect(false)
                .done(apiListener::onWaveConnected)
                .fail((d, status) -> Log.d(TAG, "Failed to connect! " + d.getName() + " " + status))
                .enqueue();
    }

    public void requestBatteryStatus() {
        manager.packetHandler.sendQuery(new Query(Query.Type.Request, Query.Id.BatteryStatus, (short) 0));
    }

    private static class ConnectionManager extends BleManager {
        private List<BluetoothGattCharacteristic> deviceCharacteristics = new ArrayList<>();
        public PacketHandler packetHandler;
        private final WaveApiListener apiListener;

        public ConnectionManager(@NonNull Context context, WaveApiListener apiListener) {
            super(context);

            this.apiListener = apiListener;
        }

        private class CustomGattCallback extends BleManagerGattCallback {
            @Override
            protected boolean isRequiredServiceSupported(@NonNull BluetoothGatt gatt) {
                BluetoothGattService someService = gatt.getService(WAVE_SERVICE_UUID);
                if (someService != null) {
                    deviceCharacteristics = someService.getCharacteristics()
                            .stream()
                            .filter(c -> c.getUuid().equals(API_CHARACTERISTIC_UUID))
                            .collect(Collectors.toList());
                }

                if (deviceCharacteristics.isEmpty()) {
                    Log.w(TAG, "Device did not have API Characteristic");
                }

                return !deviceCharacteristics.isEmpty();
            }

            private FailCallback makeFailCallback(String operation) {
                return (d, status) -> Log.e(TAG, operation + " failed with status " + status);
            }

            private class SuccessOrFail {
                public final SimpleRequest event;
                public final SuccessCallback success;
                public final FailCallback fail;

                public SuccessOrFail(SimpleRequest event, SuccessCallback success, FailCallback fail) {
                    this.event = event;
                    this.success = success;
                    this.fail = fail;
                }
            }

            private class ChainSuccesses {
                private final List<SuccessOrFail> events = new ArrayList<>();

                public ChainSuccesses() {
                }

                public ChainSuccesses then(SuccessOrFail sf) {
                    events.add(sf);
                    return this;
                }

                public void build() {
                    tryLaunchingNext(events.iterator());
                }

                private void tryLaunchingNext(Iterator<SuccessOrFail> iter) {
                    if (iter.hasNext()) {
                        SuccessOrFail next = iter.next();
                        launchAndLinkNext(next, iter);
                    }
                }

                private void launchAndLinkNext(SuccessOrFail current, Iterator<SuccessOrFail> iter) {
                    current.event.done(d -> {
                        current.success.onRequestCompleted(d);
                        tryLaunchingNext(iter);
                    }).fail(current.fail).enqueue();
                }
            }

            @Override
            protected void initialize() {
                apiCharacteristic = deviceCharacteristics
                        .stream()
                        .filter(ch -> ch.getUuid().equals(API_CHARACTERISTIC_UUID))
                        .findFirst()
                        .get(); // TODO: What if this fails?

                BluetoothGattDescriptor descriptor = apiCharacteristic.getDescriptor(CCCD_UUID);

                SuccessOrFail requestMtu = new SuccessOrFail(
                        requestMtu(MTU_TO_REQUEST),
                        d -> {
                            packetHandler = new PacketHandler(
                                    getMtu(),
                                    apiListener,
                                    packet -> {
                                        writeCharacteristic(apiCharacteristic, packet, BluetoothGattCharacteristic.WRITE_TYPE_DEFAULT)
                                                .done(dv -> packetHandler.onWriteComplete(true))
                                                .fail((dv, stat) -> Log.e(TAG, "Failed to write: " + stat))
                                                .enqueue();
                                    }
                            );

                            setNotificationCallback(apiCharacteristic).with((device, data) -> {
                                byte[] bytes = data.getValue();
                                if (bytes != null && bytes.length > 0) {
                                    packetHandler.push(bytes);
                                }
                            });
                        },
                        makeFailCallback("Request MTU = " + MTU_TO_REQUEST)
                );

                SuccessOrFail enableNotifications = new SuccessOrFail(
                        enableNotifications(apiCharacteristic),
                        d -> {
                        },
                        makeFailCallback("Enable notifications")
                );

                // TODO: May not be necessary
                SuccessOrFail writeDescriptor = new SuccessOrFail(
                        writeDescriptor(descriptor, new byte[]{0x01, 0x00}),
                        d -> {
                        },
                        makeFailCallback("Descriptor write")
                );

                new ChainSuccesses()
                        .then(requestMtu)
                        .then(enableNotifications)
                        .then(writeDescriptor)
                        .build();

            }

            @Override
            protected void onServicesInvalidated() {
                for (BluetoothGattCharacteristic c : deviceCharacteristics) {
                    disableNotifications(c);
                }

                deviceCharacteristics = new ArrayList<>();

                apiListener.onWaveDisconnected(getBluetoothDevice());
            }

            private final UUID WAVE_SERVICE_UUID = UUID.fromString("65e9296c-8dfb-11ea-bc55-0242ac130003");
            private final UUID API_CHARACTERISTIC_UUID = UUID.fromString("65e92bb1-8dfb-11ea-bc55-0242ac130003");
            private final UUID CCCD_UUID = UUID.fromString("000002902-0000-1000-8000-00805f9b34fb");

            private BluetoothGattCharacteristic apiCharacteristic;
        }

        @NonNull
        @Override
        protected BleManagerGattCallback getGattCallback() {
            return new CustomGattCallback();
        }
    }
}
