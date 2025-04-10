# Genki Wave C++ API

Here you can find C++ source code to interface with Wave by Genki. For a higher level look at the API provided, please see the [documentation](https://www.notion.so/Wave-API-8a91bd3553ee4529878342dec477d93f).

## Dependencies

The project depends on a few third-party libraries

* [JUCE](https://github.com/juce-framework/JUCE)
* [GSL](https://github.com/microsoft/GSL)
* [fmt](https://github.com/fmtlib/fmt)
* [range-v3](https://github.com/ericniebler/range-v3)
* [etl](https://github.com/ETLCPP/etl)
* [boost-ext/sml](https://github.com/boost-ext/sml)

The CMake build script uses [CPM](https://github.com/cpm-cmake/CPM.cmake) to fetch these dependencies.
If you use a different build system, you will have to make sure these libraries are available and linked properly as part of your appliation build step.

**NOTE** (Linux only): If you provide your own copy of JUCE, you'll have to apply [this patch](https://github.com/genkiinstruments/juce_bluetooth/blob/bluez-dbus/cmake/juce_Messaging_linux.cpp.patch) to hook the G-Lib mainloop up correctly. It's auto-applied if JUCE is fetched through CPM via this repo.

## Build

If using CMake, either load the project in your editor or run from the command line

```shell
cmake -B build_dir
cmake --build build_dir
```

You can specify `-DGENKI_WAVE_BUILD_EXAMPLES=OFF` during CMake configuration to disable the examples.

## Quickstart

See [juce_bluetooth](https://github.com/genkiinstruments/juce_bluetooth) for instructions on the Bluetooth API.

Once you have discovered a Wave through Bluetooth, you can instantiate a `WaveApiDevice` instance to receive data from Wave.

```c++
    listener.child_added = [&](juce::ValueTree&, juce::ValueTree& vt)
    {
        const juce::String name = vt.getProperty(ID::name);

        if (name.contains("Wave"))
        {
            const auto ble_address = vt.getProperty(ID::address).toString();
            
            wave = std::make_unique<genki::WaveApiDevice>(
                    std::make_unique<genki::BleTransport>(adapter, ble_address),
                    [](const genki::Wave::Api::Query& query, gsl::span<const gsl::byte> payload)
                    {
                        const auto id = static_cast<genki::Wave::Api::Query::Id>(query.id);
                        using Id = genki::Wave::Api::Query::Id;

                        if (id == Id::Datastream)
                        {
                            ...
                        }
                        else if (id == Id::ButtonEvent)
                        {
                            ...
                        }
                    }
            );
        }
    };
```

See the examples folder for more details.

# Known issues

* On Windows, the program might not work correctly if the Bluetooth adapter is disabled on program startup.
