cmake_minimum_required(VERSION 3.15)

project(genki-wave VERSION 0.1.0)

include(cmake/CPM.cmake)

option(GENKI_WAVE_BUILD_EXAMPLES ON "Enable genki-wave example builds")
option(GENKI_WAVE_ENABLE_JUCE_TARGETS ON "Fetch JUCE and enable JUCE-based targets")

if (GENKI_WAVE_ENABLE_JUCE_TARGETS)
    CPMAddPackage("gh:juce-framework/JUCE#8.0.3")
    CPMAddPackage("gh:genkiinstruments/juce_bluetooth#1.0.0")
endif()

CPMAddPackage("gh:microsoft/GSL#v4.0.0")
CPMAddPackage("gh:fmtlib/fmt#10.1.1")
CPMAddPackage("gh:ericniebler/range-v3#0.12.0")
CPMAddPackage("gh:ETLCPP/etl#20.38.5")
CPMAddPackage("gh:boost-ext/sml#07d159027abd1f1b2fb9ff36955f1437e3a80b23")

add_subdirectory(genki-wave)

if (GENKI_WAVE_BUILD_EXAMPLES)
    add_subdirectory(examples)
endif()