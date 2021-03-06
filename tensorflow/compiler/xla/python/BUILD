load("//tensorflow/core/platform:rules_cc.bzl", "cc_library")
load("//tensorflow/core/platform:build_config.bzl", "pyx_library")
load("//tensorflow/compiler/xla:xla.bzl", "xla_py_test_deps")
load("//tensorflow:tensorflow.bzl", "tf_cc_test")

# buildifier: disable=same-origin-load
load("//tensorflow:tensorflow.bzl", "pybind_extension")

package(
    default_visibility = [
        "//learning/pathways/data_parallel/jax:__subpackages__",
        "//tensorflow:internal",
    ],
    licenses = ["notice"],  # Apache 2.0
)

py_library(
    name = "xla_client",
    srcs = ["xla_client.py"],
    srcs_version = "PY3",
    visibility = ["//visibility:public"],
    deps = [":xla_extension"],
)

pyx_library(
    name = "custom_call_for_test",
    testonly = True,
    srcs = ["custom_call_for_test.pyx"],
)

py_test(
    name = "xla_client_backend_independent_test",
    srcs = ["xla_client_backend_independent_test.py"],
    python_version = "PY3",
    tags = ["no_oss"],  # TODO(phawkins): This test passes, but requires --config=monolithic.
    deps = [
        ":xla_client",
        ":xla_extension",
        "@absl_py//absl/testing:absltest",
    ] + xla_py_test_deps(),
)

py_library(
    name = "xla_client_test",
    testonly = 1,
    srcs = ["xla_client_test.py"],
    srcs_version = "PY3",
    deps = [
        ":custom_call_for_test",
        ":xla_client",
        ":xla_extension",
        "@absl_py//absl/flags",
        "@absl_py//absl/testing:absltest",
        "@absl_py//absl/testing:parameterized",
    ],
)

py_test(
    name = "xla_client_test_cpu",
    srcs = ["xla_client_test.py"],
    args = ["--backend=cpu"],
    main = "xla_client_test.py",
    python_version = "PY3",
    srcs_version = "PY3",
    tags = ["no_oss"],  # TODO(phawkins): This test passes, but requires --config=monolithic.
    deps = [
        ":custom_call_for_test",
        ":xla_client",
        ":xla_extension",
        "@absl_py//absl/flags",
        "@absl_py//absl/testing:absltest",
        "@absl_py//absl/testing:parameterized",
    ] + xla_py_test_deps(),
)

py_test(
    name = "xla_client_test_gpu",
    srcs = ["xla_client_test.py"],
    args = ["--backend=gpu"],
    main = "xla_client_test.py",
    python_version = "PY3",
    srcs_version = "PY3",
    tags = [
        "no_oss",
        "requires-gpu-nvidia",
    ],  # TODO(phawkins): This test passes, but requires --config=monolithic.
    deps = [
        ":xla_client",
        ":xla_extension",
        "@absl_py//absl/flags",
        "@absl_py//absl/testing:absltest",
        "@absl_py//absl/testing:parameterized",
    ] + xla_py_test_deps(),
)

cc_library(
    name = "types",
    srcs = ["types.cc"],
    hdrs = ["types.h"],
    copts = [
        "-fexceptions",
        "-fno-strict-aliasing",
    ],
    features = ["-use_header_modules"],
    deps = [
        ":bfloat16",
        "//tensorflow/compiler/xla:literal",
        "//tensorflow/compiler/xla:shape_util",
        "//tensorflow/compiler/xla:status",
        "//tensorflow/compiler/xla:status_macros",
        "//tensorflow/compiler/xla:statusor",
        "//tensorflow/compiler/xla:types",
        "//tensorflow/compiler/xla:xla_data_proto_cc",
        "//tensorflow/compiler/xla/pjrt:pjrt_client",
        "//tensorflow/core:lib",
        "//third_party/py/numpy:headers",
        "@com_google_absl//absl/container:flat_hash_map",
        "@com_google_absl//absl/container:inlined_vector",
        "@com_google_absl//absl/types:optional",
        "@pybind11",
    ],
)

cc_library(
    name = "python_ref_manager",
    srcs = ["python_ref_manager.cc"],
    hdrs = ["python_ref_manager.h"],
    copts = [
        "-fexceptions",
        "-fno-strict-aliasing",
    ],
    features = ["-use_header_modules"],
    deps = [
        "@com_google_absl//absl/base:core_headers",
        "@com_google_absl//absl/container:inlined_vector",
        "@com_google_absl//absl/synchronization",
        "@com_google_absl//absl/types:span",
        "@pybind11",
    ],
)

cc_library(
    name = "traceback",
    srcs = ["traceback.cc"],
    hdrs = ["traceback.h"],
    copts = [
        "-fexceptions",
        "-fno-strict-aliasing",
    ],
    features = ["-use_header_modules"],
    deps = [
        ":python_ref_manager",
        "//tensorflow/core:lib",
        "@com_google_absl//absl/container:inlined_vector",
        "@com_google_absl//absl/strings",
        "@com_google_absl//absl/strings:str_format",
        "@pybind11",
    ],
)

cc_library(
    name = "bfloat16",
    srcs = ["bfloat16.cc"],
    hdrs = ["bfloat16.h"],
    copts = [
        "-fexceptions",
        "-fno-strict-aliasing",
    ],
    features = ["-use_header_modules"],
    deps = [
        "//tensorflow/compiler/xla:statusor",
        "//tensorflow/compiler/xla:types",
        "//tensorflow/compiler/xla:util",
        "//tensorflow/core/platform:bfloat16",
        "//tensorflow/core/platform:logging",
        "//third_party/py/numpy:headers",
        "//third_party/python_runtime:headers",  # buildcleaner: keep
        "@com_google_absl//absl/strings",
        "@pybind11",
    ],
)

py_test(
    name = "bfloat16_test",
    srcs = ["bfloat16_test.py"],
    main = "bfloat16_test.py",
    python_version = "PY3",
    tags = ["no_oss"],
    deps = [
        ":xla_client",
        ":xla_extension",
        "@absl_py//absl/testing:absltest",
        "@absl_py//absl/testing:parameterized",
    ] + xla_py_test_deps(),
)

cc_library(
    name = "py_client",
    srcs = [
        "py_buffer.cc",
        "py_client.cc",
        "py_executable.cc",
    ],
    hdrs = [
        "py_buffer.h",
        "py_client.h",
        "py_executable.h",
    ],
    copts = [
        "-fexceptions",
        "-fno-strict-aliasing",
    ],
    features = ["-use_header_modules"],
    deps = [
        ":python_ref_manager",
        ":traceback",
        ":types",
        "//tensorflow/compiler/xla:statusor",
        "//tensorflow/compiler/xla:types",
        "//tensorflow/compiler/xla/pjrt:pjrt_client",
        "//tensorflow/core/platform:fingerprint",
        "//tensorflow/core/profiler:protos_all_cc",
        "@com_google_absl//absl/algorithm:container",
        "@com_google_absl//absl/container:flat_hash_map",
        "@com_google_absl//absl/types:optional",
        "@com_google_absl//absl/types:span",
        "@pybind11",
    ],
)

cc_library(
    name = "dlpack",
    srcs = ["dlpack.cc"],
    hdrs = ["dlpack.h"],
    copts = [
        "-fexceptions",
        "-fno-strict-aliasing",
    ],
    features = ["-use_header_modules"],
    deps = [
        ":py_client",
        ":python_ref_manager",
        ":traceback",
        "//tensorflow/compiler/xla:types",
        "//tensorflow/compiler/xla:util",
        "//tensorflow/compiler/xla/pjrt:pjrt_client",
        "//tensorflow/compiler/xla/pjrt:tracked_device_buffer",
        "//tensorflow/stream_executor:device_memory",
        "//tensorflow/stream_executor:platform",
        "//tensorflow/stream_executor/cuda:cuda_platform_id",
        "//tensorflow/stream_executor/host:host_platform_id",
        "//third_party/python_runtime:headers",  # buildcleaner: keep
        "@com_google_absl//absl/algorithm:container",
        "@com_google_absl//absl/memory",
        "@com_google_absl//absl/strings",
        "@com_google_absl//absl/types:span",
        "@dlpack",
        "@pybind11",
    ],
)

cc_library(
    name = "jax_jit",
    srcs = ["jax_jit.cc"],
    hdrs = ["jax_jit.h"],
    copts = [
        "-fexceptions",
        "-fno-strict-aliasing",
    ],
    features = ["-use_header_modules"],
    visibility = ["//visibility:private"],
    deps = [
        ":py_client",
        ":pytree",
        ":types",
        "//tensorflow/compiler/xla:shape_util",
        "//tensorflow/compiler/xla:statusor",
        "//tensorflow/compiler/xla:util",
        "//tensorflow/compiler/xla:xla_data_proto_cc",
        "//tensorflow/compiler/xla/pjrt:pjrt_client",
        "//tensorflow/core/platform:status",
        "@com_google_absl//absl/container:flat_hash_map",
        "@com_google_absl//absl/container:inlined_vector",
        "@com_google_absl//absl/synchronization",
        "@com_google_absl//absl/types:optional",
        "@pybind11",
    ],
)

cc_library(
    name = "ops",
    srcs = ["ops.cc"],
    hdrs = ["ops.h"],
    copts = [
        "-fexceptions",
        "-fno-strict-aliasing",
    ],
    features = ["-use_header_modules"],
    deps = [
        ":types",
        "//tensorflow/compiler/xla:xla_data_proto_cc",
        "//tensorflow/compiler/xla/client:xla_builder",
        "//tensorflow/compiler/xla/client:xla_computation",
        "//tensorflow/compiler/xla/client/lib:comparators",
        "//tensorflow/compiler/xla/client/lib:lu_decomposition",
        "//tensorflow/compiler/xla/client/lib:math",
        "//tensorflow/compiler/xla/client/lib:qr",
        "//tensorflow/compiler/xla/client/lib:self_adjoint_eig",
        "//tensorflow/compiler/xla/client/lib:sorting",
        "//tensorflow/compiler/xla/client/lib:svd",
        "@com_google_absl//absl/types:optional",
        "@com_google_absl//absl/types:span",
        "@pybind11",
    ],
)

cc_library(
    name = "outfeed_receiver",
    srcs = ["outfeed_receiver.cc"],
    hdrs = ["outfeed_receiver.h"],
    deps = [
        "//tensorflow/compiler/xla:literal",
        "//tensorflow/compiler/xla:shape_util",
        "//tensorflow/compiler/xla:statusor",
        "//tensorflow/compiler/xla:util",
        "//tensorflow/compiler/xla/client:xla_builder",
        "//tensorflow/compiler/xla/client:xla_computation",
        "//tensorflow/compiler/xla/pjrt:pjrt_client",
        "//tensorflow/core/profiler/lib:traceme",
        "@com_google_absl//absl/container:flat_hash_map",
        "@com_google_absl//absl/memory",
        "@com_google_absl//absl/strings:str_format",
    ],
)

tf_cc_test(
    name = "outfeed_receiver_test_cpu",
    size = "small",
    srcs = ["outfeed_receiver_test.cc"],
    deps = [
        ":outfeed_receiver",
        "//tensorflow/compiler/jit:xla_cpu_jit",
        "//tensorflow/compiler/xla:test",
        "//tensorflow/compiler/xla/client:executable_build_options",
        "//tensorflow/compiler/xla/client:xla_builder",
        "//tensorflow/compiler/xla/pjrt:cpu_device",
        "//tensorflow/compiler/xla/pjrt:pjrt_client",
        "//tensorflow/core:test",
        "//tensorflow/core:test_main",
        "@com_google_absl//absl/synchronization",
    ],
)

cc_library(
    name = "outfeed_receiver_py",
    srcs = ["outfeed_receiver_py.cc"],
    hdrs = ["outfeed_receiver_py.h"],
    copts = [
        "-fexceptions",
        "-fno-strict-aliasing",
    ],
    features = ["-use_header_modules"],
    deps = [
        ":outfeed_receiver",
        ":py_client",
        ":types",
        "//tensorflow/compiler/xla/client:xla_builder",
        "//tensorflow/compiler/xla/pjrt:pjrt_client",
        "@com_google_absl//absl/algorithm:container",
        "@com_google_absl//absl/memory",
        "@com_google_absl//absl/synchronization",
        "@pybind11",
    ],
)

# TODO(phawkins): this library is really part of JAX. Find a better home for it.
cc_library(
    name = "pytree",
    srcs = ["pytree.cc"],
    hdrs = ["pytree.h"],
    copts = [
        "-fexceptions",
        "-fno-strict-aliasing",
    ],
    features = ["-use_header_modules"],
    deps = [
        "@com_google_absl//absl/algorithm:container",
        "@com_google_absl//absl/container:flat_hash_map",
        "@com_google_absl//absl/hash",
        "@com_google_absl//absl/memory",
        "@com_google_absl//absl/strings",
        "@com_google_absl//absl/strings:str_format",
        "@pybind11",
    ],
)

cc_library(
    name = "py_traceback",
    srcs = ["py_traceback.cc"],
    hdrs = ["py_traceback.h"],
    copts = [
        "-fexceptions",
        "-fno-strict-aliasing",
    ],
    features = ["-use_header_modules"],
    deps = [
        ":traceback",
        "@com_google_absl//absl/strings:str_format",
        "@pybind11",
    ],
)

cc_library(
    name = "profiler",
    srcs = ["profiler.cc"],
    hdrs = ["profiler.h"],
    # TODO(b/172353882): figure out why compatible_with is needed to avoid some internal errors.
    compatible_with = [],
    copts = [
        "-fexceptions",
        "-fno-strict-aliasing",
    ],
    features = ["-use_header_modules"],
    deps = [
        "//tensorflow/core/profiler/lib:profiler_backends",
        "//tensorflow/core/profiler/lib:profiler_session",
        "//tensorflow/core/profiler/rpc:profiler_server_impl",
        "//tensorflow/python/profiler/internal:traceme_wrapper",
        "@pybind11",
    ],
)

cc_library(
    name = "xla_compiler",
    srcs = ["xla_compiler.cc"],
    hdrs = ["xla_compiler.h"],
    copts = [
        "-fexceptions",
        "-fno-strict-aliasing",
    ],
    features = ["-use_header_modules"],
    deps = [
        ":py_client",
        ":types",
        "//tensorflow/compiler/xla:debug_options_flags",
        "//tensorflow/compiler/xla:shape_util",
        "//tensorflow/compiler/xla:statusor",
        "//tensorflow/compiler/xla:util",
        "//tensorflow/compiler/xla:xla_data_proto_cc",
        "//tensorflow/compiler/xla/client:xla_builder",
        "//tensorflow/compiler/xla/client:xla_computation",
        "//tensorflow/compiler/xla/service:custom_call_target_registry",
        "//tensorflow/compiler/xla/service:hlo",
        "//tensorflow/compiler/xla/service:hlo_graph_dumper",
        "//tensorflow/compiler/xla/service:hlo_parser",
        "//tensorflow/compiler/xla/service:name_uniquer",
        "//tensorflow/compiler/xla/service:platform_util",
        "@com_google_absl//absl/hash",
        "@com_google_absl//absl/synchronization",
        "@com_google_absl//absl/types:optional",
        "@com_google_absl//absl/types:span",
        "@pybind11",
    ],
)

config_setting(
    name = "enable_gpu",
    define_values = {"xla_python_enable_gpu": "true"},
)

pybind_extension(
    name = "xla_extension",
    srcs = [
        "xla.cc",
    ],
    copts = [
        "-fexceptions",
        "-fno-strict-aliasing",
    ],
    features = ["-use_header_modules"],
    module_name = "xla_extension",
    deps = [
        ":bfloat16",
        ":dlpack",
        ":jax_jit",
        ":ops",
        ":profiler",
        ":py_client",
        ":pytree",
        ":python_ref_manager",
        ":py_traceback",
        ":outfeed_receiver_py",
        ":types",
        ":xla_compiler",
        "@com_google_absl//absl/base",
        "@com_google_absl//absl/hash",
        "@com_google_absl//absl/memory",
        "@com_google_absl//absl/strings",
        "@com_google_absl//absl/synchronization",
        "@com_google_absl//absl/types:optional",
        "@com_google_absl//absl/types:span",
        "//third_party/py/numpy:headers",
        "@pybind11",
        "//third_party/python_runtime:headers",  # buildcleaner: keep
        "//tensorflow/compiler/xla:literal",
        "//tensorflow/compiler/xla:shape_util",
        "//tensorflow/compiler/xla:status",
        "//tensorflow/compiler/xla:statusor",
        "//tensorflow/compiler/xla:types",
        "//tensorflow/compiler/xla:util",
        "//tensorflow/compiler/xla/client:client_library",
        "//tensorflow/compiler/xla/client:executable_build_options",
        "//tensorflow/compiler/xla/client:local_client",
        "//tensorflow/compiler/xla/pjrt:cpu_device",
        "//tensorflow/compiler/xla/pjrt:interpreter_device",
        "//tensorflow/compiler/xla/pjrt:gpu_device",
        "//tensorflow/compiler/xla/pjrt:pjrt_client",
        "//tensorflow/compiler/xla/pjrt:tpu_client",
        "//tensorflow/compiler/xla/pjrt:tracked_device_buffer",
        "//tensorflow/compiler/xla/pjrt/distributed",
        "//tensorflow/compiler/xla/pjrt/distributed:client",
        "//tensorflow/compiler/xla/pjrt/distributed:service",
        "//tensorflow/compiler/xla/service:computation_placer",
        "//tensorflow/compiler/xla/service:name_uniquer",
        "//tensorflow/compiler/xla/service:platform_util",
        "//tensorflow/compiler/xla/service:shaped_buffer",
        "//tensorflow/compiler/xla/service:transfer_manager",
        "//tensorflow/compiler/xla/service:cpu_plugin",
        "//tensorflow/core:lib",
        # Do NOT remove this dependency. The XLA Python extension must not
        # depend on any part of TensorFlow at runtime, **including**
        # libtensorflow_framework.so. The XLA module is deployed self-contained
        # without any TF dependencies as "jaxlib" on Pypi, and "jaxlib" does
        # not require Tensorflow.
        "//tensorflow/core:lib_internal_impl",  # buildcleaner: keep
        "//tensorflow/stream_executor:device_memory_allocator",
        "//tensorflow/stream_executor:platform",
    ] + select({
        ":enable_gpu": ["//tensorflow/compiler/xla/service:gpu_plugin"],
        "//conditions:default": [],
    }),
)
