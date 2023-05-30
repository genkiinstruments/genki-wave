#pragma once

#ifdef __clang__
#pragma clang diagnostic push
#pragma clang diagnostic ignored "-Wextra-semi"
#pragma clang diagnostic ignored "-Wswitch-enum"
#endif

#include <fmt/ranges.h>

#ifdef __clang__
#pragma clang diagnostic pop
#endif

#include <juce_core/juce_core.h>

#include "wave_public_types.h"

template<>
struct fmt::formatter<juce::String>
{
    constexpr auto parse(fmt::format_parse_context& ctx) -> decltype(ctx.begin()) { return ctx.begin(); }

    template<typename FormatContext>
    auto format(const juce::String& str, FormatContext& ctx) -> decltype(ctx.out()) { return fmt::format_to(ctx.out(), "{}", str.getCharPointer().getAddress()); }
};

template<>
struct fmt::formatter<const gsl::byte>
{
    constexpr auto parse(fmt::format_parse_context& ctx) -> decltype(ctx.begin()) { return ctx.begin(); }

    template<typename FormatContext>
    auto format(const gsl::byte& byte, FormatContext& ctx) -> decltype(ctx.out())
    {
        return fmt::format_to(ctx.out(), "{:02x}", static_cast<const unsigned char>(byte));
    }
};

template<>
struct fmt::formatter<genki::Wave::ButtonEvent>
{
    constexpr auto parse(fmt::format_parse_context& ctx) -> decltype(ctx.begin()) { return ctx.begin(); }

    template<typename FormatContext>
    auto format(const genki::Wave::ButtonEvent& evt, FormatContext& ctx) -> decltype(ctx.out())
    {
        constexpr std::array<std::string_view, 4> names{"A", "B", "C", "D"};
        constexpr std::array<std::string_view, 8> actions{"Up", "Down", "Long", "LongUp", "ExtraLong", "ExtraLongUp", "Click", "DoubleClick"};

        return fmt::format_to(ctx.out(), "{{ {}, {} }}", names[(size_t) evt.id], actions[(size_t) evt.action]);
    }
};

template <>
struct fmt::formatter<genki::Wave::Api::Query>
{
    constexpr auto parse(fmt::format_parse_context& ctx) -> decltype(ctx.begin()) { return ctx.begin(); }

    template<typename FormatContext>
    auto format(const genki::Wave::Api::Query& q, FormatContext& ctx) -> decltype(ctx.out())
    {
        return fmt::format_to(ctx.out(), "{{ type: {}, id: {}, payload_size: {} }}", (int) q.type, (int) q.id, (int) q.payload_size);
    }
};

template<>
struct fmt::formatter<genki::Wave::Version>
{
    constexpr auto parse(fmt::format_parse_context& ctx) -> decltype(ctx.begin()) { return ctx.begin(); }

    template<typename FormatContext>
    auto format(const genki::Wave::Version& v, FormatContext& ctx) -> decltype(ctx.out())
    {
        return fmt::format_to(ctx.out(), "{}.{}.{}", v.major, v.minor, v.patch);
    }
};

