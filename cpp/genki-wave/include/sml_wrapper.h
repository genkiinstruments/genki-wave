#pragma once

#ifdef __clang__
#pragma clang diagnostic push
#pragma clang diagnostic ignored "-Wzero-as-null-pointer-constant"
#pragma clang diagnostic ignored "-Wshadow-field-in-constructor"
#pragma clang diagnostic ignored "-Wshadow-field"
#pragma clang diagnostic ignored "-Wsign-conversion"
#endif

#include "boost/sml.hpp"

#ifdef __clang__
#pragma clang diagnostic pop
#endif