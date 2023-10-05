cmake_minimum_required(VERSION 3.15)

project(genki-wave VERSION 0.1.0)

include(cmake/fetch_from_git.cmake)

option(GENKI_WAVE_BUILD_EXAMPLES ON "Enable genki-wave example builds")
option(GENKI_WAVE_ENABLE_TESTING ON "Enable tests for genki-wave")
option(GENKI_WAVE_ENABLE_JUCE_TARGETS ON "Fetch JUCE and enable JUCE-based targets")

if (GENKI_WAVE_ENABLE_JUCE_TARGETS)
    fetch_from_git(JUCE https://github.com/juce-framework/JUCE.git SOURCE_DIRECTORY_VAR juce_source_dir)
    fetch_from_git(juce_bluetooth https://github.com/genkiinstruments/juce_bluetooth.git GIT_TAG main)
endif()

fetch_from_git(gsl https://github.com/microsoft/GSL.git GIT_TAG main)
fetch_from_git(etl https://github.com/ETLCPP/etl.git)
fetch_from_git(fmt https://github.com/fmtlib/fmt.git)
fetch_from_git(range-v3 https://github.com/ericniebler/range-v3.git)
fetch_from_git(sml https://github.com/boost-ext/sml.git SOURCE_DIRECTORY_VAR sml_source_dir)

if (GENKI_WAVE_ENABLE_TESTING)
    fetch_from_git(ut https://github.com/boost-ext/ut.git)
    add_subdirectory(tests)
endif()

add_subdirectory(genki-wave)

if (GENKI_WAVE_BUILD_EXAMPLES)
    add_subdirectory(examples)
endif()