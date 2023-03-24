# Genki Wave Android library

Genki Wave can be easily integrated into your Android app. For a higher level look at the API provided, please see the [documentation](https://www.notion.so/Wave-API-8a91bd3553ee4529878342dec477d93f).

## Dependencies

The project relies on [Android Studio](https://developer.android.com/studio) and [CMake]([https://developer.android.com/studio](https://cmake.org/)) to build.

## Build

It's easiest to start with the examle app found in the examples folder.

To integrate genki-wave into your app you need to take the following steps

1. In your app's root, locate `gradle.settings` and put the following 
```
include ':genki-wave'
project(':genki-wave').projectDir = new File('path/to/genki-wave/library')
```
2. In your app's `build.gradle` (not the top-level one), locate the dependencies section, and add
```
dependencies {
    ...
    implementation project(path: ':genki-wave')
}
```
