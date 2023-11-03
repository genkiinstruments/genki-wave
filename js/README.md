# Genki Wave Node.js module

## Provides a simple wrapper to connect to Wave by Genki through Node.js

Note: The module is provided in an experimental state. All feedback greatly appreciated through issues or PRs.

### How to build

(temporary) Make sure you have the latest [webbluetooth](https://github.com/thegecko/webbluetooth) sources, and build the library.
```shell
git submodule update --init --recursive
pushd genki-wave/webbluetooth && pnpm i && pnpm prebuild && pnpm tsc ; popd
```

Build the `genki-wave` module

```shell
pushd genki-wave && pnpm install && pnpm build ; popd
```

Check out the [examples](./examples) folder for examples on how to use the module.
