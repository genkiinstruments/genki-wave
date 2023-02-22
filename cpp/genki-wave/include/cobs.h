#pragma once

#include <algorithm>
#include <cstddef>
#include <cstdint>
#include <gsl/byte>
#include <optional>

namespace genki {

constexpr size_t cobs_encoded_size(size_t decoded_size) { return decoded_size + 2; }

template<typename InputIt, typename OutputIt>
auto cobs_encode(InputIt in_begin, InputIt in_end, OutputIt out_begin) -> OutputIt
{
    // The output iterator must be random access in order for this function to work properly.
    // Could potentially be refactored to accept e.g. a std::back_inserter and such iterators
    static_assert(std::is_same_v<typename std::iterator_traits<OutputIt>::iterator_category, std::random_access_iterator_tag>);

    auto    in       = in_begin;
    auto    out      = out_begin++;
    auto    code_pos = out++;
    uint8_t code     = 1;

    while (in != in_end)
    {
        if (*in != gsl::byte(0))
        {
            *out++ = *in;
            ++code;
        }

        if (*in == gsl::byte(0) || code == 0xFF)
        {
            *code_pos = gsl::byte(code);
            code_pos = out++;
            code = 1;
        }

        ++in;
    }

    *code_pos = gsl::byte(code);
    *out++    = gsl::byte(0);

    return out;
}

template<typename InputIt, typename OutputIt>
auto cobs_decode(InputIt in_begin, InputIt in_end, OutputIt out_begin) -> OutputIt
{
    auto      in             = in_begin;
    auto      out            = out_begin;
    size_t    cur_block_size = 0;
    auto code           = gsl::byte(0xFF);

    while (in != in_end && *in != gsl::byte(0x00))
    {
        if (cur_block_size > 0)
        {
            *out++ = *in++;
        }
        else
        {
            if (code != gsl::byte(0xFF))
            {
                *out++ = gsl::byte(0);
            }

            code           = *in++;
            cur_block_size = static_cast<uint8_t>(code);
        }

        --cur_block_size;
    }

    return out;
}

template<typename It>
auto find_cobs_packet(const It start, const It end, gsl::byte delimiter = gsl::byte(0x00)) -> std::optional<std::pair<It, It>>
{
    const auto end_token = std::find(start, end, delimiter);

    return end_token != end
           ? std::optional(std::make_pair(start, end_token + 1))
           : std::nullopt;
}

} // namespace genki
