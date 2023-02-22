#pragma once

#include <array>
#include <cassert>
#include <cstdint>
#include <cstring>
#include <string_view>
#include <tuple>

#ifdef __GNUC__
#define GCC_PACK __attribute__((__packed__))
#endif

#ifdef _MSC_VER
#define GCC_PACK
#endif


namespace genki::Wave {
//======================================================================================================================
enum class DeviceMode : std::uint8_t
{
    Standalone = 100,
    Softwave,
    Wavefront,
    Api,
    Work,
    Init,
};

namespace Api {
//======================================================================================================================
enum class QueryType : std::uint8_t { Request = 1, Response, Stream, MAX_VAL };

struct Query
{
    using Type = QueryType;

    enum class Id : std::uint8_t
    {
        Datastream = 1,
        BatteryStatus,
        DeviceInfo,
        ButtonEvent,
        DeviceMode,
        Identify,
        Recenter,
        DisplayFrame,
        RawSensorData,
        SpectrogramData,
        ModifyApiConfig,
        MAX_VAL
    };

    const Type     type{};
    const Id       id{};
    const uint16_t payload_size{};
};

enum class DatastreamType : std::uint8_t
{
    None       = 0,
    MotionData = 1,
    RawData    = 2,
};

struct Config
{
    DatastreamType datastream_type;
    bool           spectrogram_enabled;
    float          sample_rate;
};

} // namespace Api

//======================================================================================================================
template<size_t max_size>
class String
{
private:
    std::array<char, max_size + 1> chars{};

public:
    constexpr String() = default;

    explicit String(const char* s) { std::memcpy(chars.data(), s, strnlen(s, max_size)); }

    explicit String(std::string_view s)
    {
        assert(s.size() <= max_size);
        std::memcpy(chars.data(), s.data(), s.size());
    }

    [[nodiscard]] const char* c_str() const { return chars.data(); }

    [[nodiscard]] size_t length() const { return strnlen(chars.data(), max_size); }

    bool operator==(const String& rhs) const
    {
        const auto len = rhs.length();
        return len == length() && std::strncmp(chars.data(), rhs.chars.data(), len) == 0;
    }

    bool operator!=(const String& rhs) const { return !(*this == rhs); }
};

//======================================================================================================================
// Using semantic versioning format
struct Version
{
    uint8_t major, minor, patch;

    [[nodiscard]] constexpr uint32_t as_number() const { return (uint32_t) ((major << 16u) | (minor << 8u) | (patch << 0u)); }

    static constexpr Version from_number(uint32_t n)
    {
        return {
                .major = (uint8_t) (n >> 16u),
                .minor = (uint8_t) (n >> 8u),
                .patch = (uint8_t) (n >> 0u),
        };
    }

    constexpr bool operator!=(const Version& other) const { return (patch != other.patch) || (minor != other.minor) || (major != other.major); }
    constexpr bool operator==(const Version& other) const { return !(*this != other); }
    constexpr bool operator>=(const Version& other) const { return *this > other || *this == other; }
    constexpr bool operator<=(const Version& other) const { return *this < other || *this == other; }
    constexpr bool operator>(const Version& other) const { return other < *this; }
    constexpr bool operator<(const Version& other) const
    {
        return (major < other.major)
               || (major == other.major && minor < other.minor)
               || (major == other.major && minor == other.minor && patch < other.patch);
    }
};

struct MacAddress
{
    static constexpr int      Size = 6;
    std::array<uint8_t, Size> data;

    MacAddress() = default;

    explicit MacAddress(const std::array<uint8_t, Size>& a) : data({a[0], a[1], a[2], a[3], a[4], a[5]}) {}

    explicit MacAddress(const uint8_t a[Size]) : data({a[0], a[1], a[2], a[3], a[4], a[5]}) {}

    bool operator==(const MacAddress& other) const { return data == other.data; }
};

namespace Constants {
static constexpr uint8_t SerialNumberLength = 16;
static constexpr uint8_t BoardVersionLength = 8;
}

using SerialNumber = String<Constants::SerialNumberLength>;
using BoardVersion = String<Constants::BoardVersionLength>;

struct DeviceInfo
{
    Version      firmware_version;
    BoardVersion board_version;

    MacAddress bluetooth_address;

    SerialNumber serial_number;
};

//======================================================================================================================
enum class ButtonId : std::uint8_t { A, B, C, D };

enum class ButtonAction : std::uint8_t
{
    Up,
    Down,
    Long,
    LongUp,
    ExtraLong,
    ExtraLongUp,
    Click,
    DoubleClick,
};

struct ButtonEvent
{
    ButtonId     id;
    ButtonAction action;
    float        timestamp{};

    bool operator==(const ButtonEvent& rhs) const { return id == rhs.id && action == rhs.action; }
    bool operator<(const ButtonEvent& rhs) const { return std::tie(id, action) < std::tie(rhs.id, rhs.action); }
};

struct BatteryStatus { float voltage, percentage; bool is_charging; };

#ifdef _MSC_VER
__pragma( pack(push, 1) )
#endif

struct GCC_PACK Datastream
{
    struct GCC_PACK SensorData
    {
        std::array<float, 3> gyro, accel, mag;
    } data;

    struct GCC_PACK MotionData
    {
        std::array<float, 4> rawPose, currentPose;
        std::array<float, 3> euler;
        std::array<float, 3> linearAccel;

        struct GCC_PACK Peak
        {
            bool  detected;
            float normVelocity;
        };

        Peak tap;

    } motionData;

    uint64_t timestamp_us;
};

#if defined(_MSC_VER)
using float16_t = __bfloat16;
#elif defined(__arm__)
using float16_t = __fp16;
#endif

using float32_t = float;

#define SPECTROGRAM_PRECISION 32

#define _FLOAT_PRECISION(precision) float ## precision ## _t
#define FLOAT_PRECISION(precision) _FLOAT_PRECISION(precision)

using SpectrogramPrecision = FLOAT_PRECISION(SPECTROGRAM_PRECISION); // float16_t or float32_t

struct GCC_PACK SpectrogramDatastream
{
    constexpr static auto num_channels = 6;
    constexpr static auto num_bins = 16;

    using Column = std::array<SpectrogramPrecision, num_bins>;
    struct GCC_PACK Data
    {
        Column acc_x, acc_y, acc_z, gyro_x, gyro_y, gyro_z;
    };

    union GCC_PACK
    {
        Data columns;
        std::array<Column, num_channels> flat;
    } data;

    uint64_t timestamp_us;
};

#ifdef _MSC_VER
__pragma( pack(pop) )
#endif

//======================================================================================================================
struct MidiEvent
{
    uint8_t cc{}, value{};
};

//======================================================================================================================
struct Pixel
{
    uint8_t row{}, column{};
};

//======================================================================================================================
template<typename Type>
struct Range
{
    Type min, max;

    constexpr Range<Type> inverted() const { return {max, min}; }

    template<typename NewType>
    constexpr Range<NewType> to() const { return {static_cast<NewType>(min), static_cast<NewType>(max)}; }
};

using Rangef = Range<float>;
using Ranged = Range<double>;
using Rangei = Range<int>;

enum class Orientation : uint8_t { Left, Right };

} // namespace genki::Wave
