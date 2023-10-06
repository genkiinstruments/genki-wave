var lib = require('bindings')('packethandler');

import {Bluetooth,} from "webbluetooth"
import {EventEmitter} from "eventemitter3";

const WAVE_API_SERVICE_UUID = "65e9296c-8dfb-11ea-bc55-0242ac130003";
const WAVE_API_CHARACTERISTIC_UUID = "65e92bb1-8dfb-11ea-bc55-0242ac130003";

type DeviceCallback = (device: BluetoothDevice) => boolean

export enum QueryType {
    Request = 1,
    Response,
    Stream,
}

export enum QueryId {
    Datastream = 1,
    BatteryStatus,
    DeviceInfo,
    ButtonEvent,
    DeviceMode,
    Identify,
    Recenter,
    DisplayFrame,
}

export type Query = {
    type: QueryType,
    id: QueryId,
    payloadSize?: number
};

export type Wave = {
    server: BluetoothRemoteGATTServer,
    emitter: EventEmitter,
    packet_handler: typeof lib.PacketHandler,
};

export async function discover(deviceFound: DeviceCallback, timeout?: number) {

    const bluetooth = new Bluetooth({deviceFound, scanTime: timeout});
    return await bluetooth.requestDevice({acceptAllDevices: true});
}

export async function connect(device: BluetoothDevice): Promise<{ wave?: Wave, error?: string }> {
    const server = await device.gatt?.connect();

    if (!server) return {error: "Failed to connect"};

    const {id, name} = server.device;
    console.log(`connected to ${name} (${id})`);

    const services = await server.getPrimaryServices();
    const api_service = await services.find(service => service.uuid === WAVE_API_SERVICE_UUID)
    if (!api_service) return {error: "API service not found"};

    const api_charact = (await api_service.getCharacteristics()).find(charact => charact.uuid === WAVE_API_CHARACTERISTIC_UUID)
    if (!api_charact) return {error: "API characteristic not found"};

    await api_charact.startNotifications();
    console.log("notifications started");

    const emitter = new EventEmitter()

    const packet_handler = new lib.PacketHandler(emitter.emit.bind(emitter), (data: ArrayBuffer) => {
        api_charact.writeValueWithResponse(data);
    });

    api_charact.addEventListener("characteristicvaluechanged", (event) => {
        // @ts-ignore
        packet_handler.pushBytes(event.target?.value.buffer);
    });

    return {
        wave: {
            server,
            emitter,
            packet_handler,
        }
    };
}

export function disconnect(wave: Wave) {
    wave.server.disconnect();
}