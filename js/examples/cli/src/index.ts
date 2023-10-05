import { Bluetooth } from "webbluetooth"
import {EventEmitter} from "events";
import {PacketHandler} from "./addon";

const emitter = new EventEmitter()
const emit = emitter.emit.bind(emitter);

let packet_handler: typeof PacketHandler | null;

emitter.on('data', (data) => {
    console.log('### DATA:', data);
})

emitter.on('button', (button) => {
    console.log('### BUTTON:', button);
})

emitter.on('battery', (battery) => {
    console.log('### BATTERY:', battery);
})

const WAVE_API_SERVICE_UUID = "65e9296c-8dfb-11ea-bc55-0242ac130003";
const WAVE_API_CHARACTERISTIC_UUID = "65e92bb1-8dfb-11ea-bc55-0242ac130003";

const deviceFound = (bluetoothDevice, selectFn) => {
    if (bluetoothDevice.name === "Wave") return true;
}

const enumerateGatt = async server => {
    const services = await server.getPrimaryServices();
    const sPromises = services.map(async service => {
        const characteristics = await service.getCharacteristics();
        const cPromises = characteristics.map(async characteristic => {
            let descriptors = await characteristic.getDescriptors();
            descriptors = descriptors.map(descriptor => `\t\t└descriptor: ${descriptor.uuid}`);
            descriptors.unshift(`\t└characteristic: ${characteristic.uuid}`);
            return descriptors.join("\n");
        });

        const descriptors = await Promise.all(cPromises);
        descriptors.unshift(`service: ${service.uuid}`);
        return descriptors.join("\n");
    });

    const result = await Promise.all(sPromises);
    console.log(result.join("\n"));

    const api_service = await services.find(service => service.uuid === WAVE_API_SERVICE_UUID)
    const api_charact = (await api_service.getCharacteristics()).find(charact => charact.uuid === WAVE_API_CHARACTERISTIC_UUID)

    await api_charact.startNotifications();
    console.log("Notifications started");

    packet_handler = new PacketHandler(emit, (data: ArrayBuffer) => {
        api_charact.writeValueWithResponse(data);
    });

    api_charact.addEventListener("characteristicvaluechanged", event => {
        packet_handler.pushBytes(event.target.value?.buffer);
    });
};

const bluetooth = new Bluetooth({deviceFound: (device, selectFn): boolean => {
        return device.name === "Wave";
    }
});

(async () => {
    try {
        console.log("scanning...")

        const device = await bluetooth.requestDevice({ acceptAllDevices: true });

        console.log("connecting...");

        const server = await device.gatt.connect();
        const {id, address, name} = server.device;
        console.log(`connected to ${name} (${id || address})`);

        await enumerateGatt(server);

        var should_exit = false;

        process.on('SIGINT', () => { should_exit = true; });

        // Request battery level every 1 second
        setInterval(() => {
            packet_handler.sendQuery({
                'type': 'request',
                'id': 2,
                'payload_size': 0
            })
        }, 1000);

        while (!should_exit) {
            await new Promise(resolve => setTimeout(resolve, 500));
        }

        server.disconnect();

        console.log("\ndisconnected");
    } catch (error) {
        console.log('ah!', error);
    }

    console.log('fin')
    process.exit(0);
})();