cmake_minimum_required(VERSION 3.15)
set(CMAKE_CXX_STANDARD 17)

project(wave_api_stream VERSION 0.1.0)
set(target ${PROJECT_NAME})

juce_add_console_app(${target})

target_sources(${target}
        PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}/src/main.cpp
        )

target_compile_definitions(${target}
        PRIVATE
        JUCE_MODAL_LOOPS_PERMITTED=1
        )

target_link_libraries(${target}
        PRIVATE
        genki-wave

        PUBLIC
        juce::juce_recommended_config_flags
        juce::juce_recommended_warning_flags
        )

