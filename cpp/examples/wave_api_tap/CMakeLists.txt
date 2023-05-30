cmake_minimum_required(VERSION 3.15)

if (WIN32)
    set(CMAKE_CXX_STANDARD 20)
else ()
    set(CMAKE_CXX_STANDARD 17)
endif ()

project(wave_api_tap VERSION 0.1.0)
set(target ${PROJECT_NAME})

juce_add_gui_app(${target})

target_sources(${target} PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/src/main.cpp)

target_compile_definitions(${target}
        PRIVATE
        JUCE_WEB_BROWSER=0
        JUCE_USE_CURL=0
        JUCE_APPLICATION_NAME_STRING="wave_api_tap_example"
        JUCE_APPLICATION_VERSION_STRING="${PROJECT_VERSION}"
        )

target_link_libraries(${target}
        PRIVATE
        genki-wave
        juce::juce_gui_extra

        PUBLIC
        juce::juce_recommended_config_flags
        juce::juce_recommended_lto_flags
        juce::juce_recommended_warning_flags
        )
