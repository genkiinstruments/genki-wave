{
  "targets": [
    {
      "target_name": "addon",
      "cflags!": [ "-fno-exceptions" ],
      "cflags_cc!": [ "-fno-exceptions" ],
      "sources": [ "src/cpp/addon.cpp", "src/cpp/packet_handler.cpp" ],
      "include_dirs": [
        "<!@(node -p \"require('node-addon-api').include\")",
        "../../../cpp/genki-wave/include",
        "build/etl/include",
        "build/gsl/include",
        "build/sml/include",
        "build/fmt/include",
      ],
      'defines': [
        'NAPI_DISABLE_CPP_EXCEPTIONS',
        'FMT_HEADER_ONLY'
        ],
    }
  ]
}