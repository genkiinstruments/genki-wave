#include <juce_gui_extra/juce_gui_extra.h>
#include <memory>
#include <range/v3/view.hpp>

#include "ble_transport.h"
#include "wave_api_device.h"
#include "format.h"

//======================================================================================================================
class MainComponent : public juce::Component,
                      private juce::ValueTree::Listener
{
public:
    //==================================================================================================================
    MainComponent()
    {
        adapter.state.addListener(this);

        addAndMakeVisible(tap_sensitivity);
        addAndMakeVisible(label);

        tap_sensitivity.setRange(0.0, 1.0);
        tap_sensitivity.setValue(0.7, juce::dontSendNotification);

        label.setFont(24.0f);
        label.setJustificationType(juce::Justification::centred);

        tap_sensitivity.onDragEnd = [this] { updateApiConfig(); };

        setSize(300, 200);
    }

    //==================================================================================================================
    void paint(juce::Graphics&) override {}

    void resized() override
    {
        auto r = getLocalBounds();
        tap_sensitivity.setBounds(r.removeFromBottom(40));
        label.setBounds(r);
    }

private:
    //==================================================================================================================
    void valueTreePropertyChanged(juce::ValueTree& vt, const juce::Identifier& id) override
    {
        if (vt.hasType(ID::BLUETOOTH_ADAPTER) && id == ID::status)
        {
            const auto is_powered_on = AdapterStatus((int) vt.getProperty(id)) == AdapterStatus::PoweredOn;

            fmt::print("{}\n", is_powered_on
                               ? "Adapter powered on, starting scan..."
                               : "Adapter powered off/disabled, stopping scan...");

            adapter.scan(is_powered_on);
        }
        else if (vt.hasType(ID::BLUETOOTH_DEVICE) && id == ID::last_seen)
        {
            if (vt.getProperty(ID::name).toString().isNotEmpty())
            {
                fmt::print("{} {} - rssi: {}\n",
                        vt.getProperty(ID::name).toString().toStdString(),
                        vt.getProperty(ID::address).toString().toStdString(),
                        (int) vt.getProperty(ID::rssi));
            }
        }
    }

    void valueTreeChildAdded(juce::ValueTree&, juce::ValueTree& vt) override
    {
        const juce::String name = vt.getProperty(ID::name);

        // Note: Should preferably match on a BLE address instead...
        if (name.contains("Wave"))
        {
            fmt::print("Found device: {} connecting...\n", name);
            const auto ble_address = vt.getProperty(ID::address).toString();

            wave = std::make_unique<genki::WaveApiDevice>(
                    std::make_unique<genki::BleTransport>(adapter, ble_address),
                    [&](const genki::Wave::Api::Query& query, gsl::span<const gsl::byte> payload)
                    {
                        const auto id = static_cast<genki::Wave::Api::Query::Id>(query.id);
                        using Id = genki::Wave::Api::Query::Id;

                        if (id == Id::DeviceInfo)
                        {
                            const auto& info = genki::copy<genki::Wave::DeviceInfo>(payload);

                            const auto required_firmware_version = genki::Wave::Version{1, 7, 5};

                            if (info.firmware_version < required_firmware_version)
                            {
                                fmt::print("Incompatible firmware version: {}, required: {}\n", info.firmware_version, required_firmware_version);
                                return;
                            }

                            updateApiConfig();
                        }
                        else if (id == Id::Datastream)
                        {
                            const auto& ds = genki::copy<genki::Wave::Datastream>(payload);

                            if (const auto& [detected, velocity] = ds.motionData.tap; detected)
                            {
                                fmt::print("Tap detected: {}\n", velocity);

                                label.setText("TAP", juce::dontSendNotification);

                                juce::Timer::callAfterDelay(200, [this] { label.setText("", juce::dontSendNotification); });
                            }
                        }
                    }
            );

            // Assume Wave has been successfully connected after a short while.
            // Ideally you'd want to keep track of the connection state and send commands once connection has been
            // established and the characteristics discovered.
            juce::Timer::callAfterDelay(1000, [&] { wave->request_info(); });

            adapter.scan(false);
        }
    }

    //==================================================================================================================
    void updateApiConfig()
    {
        if (wave != nullptr)
        {
            wave->updateConfig({
                    .datastream_type = genki::Wave::Api::DatastreamType::MotionData,
                    .sample_rate = 400.0f, // Required for best performance
                    .tap_sensitivity = static_cast<float>(tap_sensitivity.getValue()),
            });
        }
    }

    //==================================================================================================================
    genki::BleAdapter                     adapter;
    std::unique_ptr<genki::WaveApiDevice> wave;

    juce::Label  label{};
    juce::Slider tap_sensitivity{juce::Slider::LinearHorizontal, juce::Slider::NoTextBox};

    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR (MainComponent)
};

//======================================================================================================================
// JUCE boilerplate for launching a GUI application...
class GuiAppApplication : public juce::JUCEApplication
{
public:
    //==================================================================================================================
    GuiAppApplication() {}

    const juce::String getApplicationName() override { return JUCE_APPLICATION_NAME_STRING; }
    const juce::String getApplicationVersion() override { return JUCE_APPLICATION_VERSION_STRING; }
    bool moreThanOneInstanceAllowed() override { return true; }

    //==================================================================================================================
    void initialise(const juce::String&) override { mainWindow = std::make_unique<MainWindow>(getApplicationName()); }
    void shutdown() override { mainWindow = nullptr; }

    //==================================================================================================================
    void systemRequestedQuit() override { quit(); }
    void anotherInstanceStarted(const juce::String&) override {}

    //==================================================================================================================
    class MainWindow : public juce::DocumentWindow
    {
    public:
        explicit MainWindow(const juce::String& name)
                : DocumentWindow(name,
                juce::Desktop::getInstance().getDefaultLookAndFeel().findColour(ResizableWindow::backgroundColourId),
                DocumentWindow::allButtons)
        {
            setUsingNativeTitleBar(true);
            setContentOwned(new MainComponent(), true);

#if JUCE_IOS || JUCE_ANDROID
            setFullScreen (true);
#else
            setResizable(true, true);
            centreWithSize(getWidth(), getHeight());
#endif

            setVisible(true);
        }

        void closeButtonPressed() override
        {
            JUCEApplication::getInstance()->systemRequestedQuit();
        }

    private:
        JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR (MainWindow)
    };

private:
    std::unique_ptr<MainWindow> mainWindow;
};

//======================================================================================================================
// This macro generates the main() routine that launches the app.
START_JUCE_APPLICATION (GuiAppApplication)
