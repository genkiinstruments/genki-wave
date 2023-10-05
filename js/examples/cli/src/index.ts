import {connect, disconnect, discover} from "./genki-wave"

(async () => {
    console.log("scanning...")
    const found = await discover(({name}) => name == "Wave")

    console.log("connecting...");
    const {wave, error} = await connect(found);

    if (error || !wave) {
        console.error(error ?? "oops");
        process.exit(1);
    }

    wave.emitter.on('data', (data) => { console.log('### DATA:', data); })
    wave.emitter.on('button', (button) => { console.log('### BUTTON:', button); })
    wave.emitter.on('battery', (battery) => { console.log('### BATTERY:', battery); })

    var should_exit = false;
    process.on('SIGINT', () => { should_exit = true; });

    // Request battery level every 1 second
    setInterval(() => {
        // TODO: Wrap Query and IDs in JS
        wave.packet_handler.sendQuery({
            'type': 'request',
            'id': 2,
            'payload_size': 0
        })
    }, 1000);

    while (!should_exit) {
        await new Promise(resolve => setTimeout(resolve, 500));
    }

    disconnect(wave);
    console.log("\ndisconnected");

    console.log('fin')
    process.exit(0);
})();
