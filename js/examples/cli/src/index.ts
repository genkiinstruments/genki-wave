import { Bluetooth } from "webbluetooth"

import {PacketHandler} from "./addon";

const obj = new PacketHandler();

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

    api_charact.addEventListener("characteristicvaluechanged", event => {
        obj.pushBytes(event.target.value?.buffer);
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