## Build

To build webbluetooth (until a new version is published on npm)
```
git submodule update --init --recursive
pushd webbluetooth && pnpm i && pnpm prebuild && pnpm tsc ; popd
```

Then you should be good to go
```
pnpm install && pnpm build
```
