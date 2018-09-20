cmake_minimum_required(VERSION 2.7)

project(xz C)

if (MSVC_VERSION LESS 1900)
    message("only MSVC v14 or later are supported by this CMake file")
    set(CMAKE_PDB_OUTPUT_DIRECTORY_RELWITHDEBINFO ${CMAKE_PDB_OUTPUT_DIRECTORY_RELWITHDEBINFO})
    return ()
ENDIF ()

# general C flags
set (CMAKE_C_FLAGS "${CMAKE_C_FLAGS} /DHAVE_CONFIG_H /DWIN32 /DDLL_EXPORT /DNDEBUG /D_WINDOWS /D_USRDLL /DLIBLZMADLL_EXPORTS")

set (SOURCES src/common/tuklib_cpucores.c
             src/common/tuklib_physmem.c
             src/liblzma/check/check.c
             src/liblzma/check/crc32_fast.c
             src/liblzma/check/crc32_table.c
             src/liblzma/check/crc64_fast.c
             src/liblzma/check/crc64_table.c
             src/liblzma/check/sha256.c
             src/liblzma/common/alone_decoder.c
             src/liblzma/common/alone_encoder.c
             src/liblzma/common/auto_decoder.c
             src/liblzma/common/block_buffer_decoder.c
             src/liblzma/common/block_buffer_encoder.c
             src/liblzma/common/block_decoder.c
             src/liblzma/common/block_encoder.c
             src/liblzma/common/block_header_decoder.c
             src/liblzma/common/block_header_encoder.c
             src/liblzma/common/block_util.c
             src/liblzma/common/common.c
             src/liblzma/common/easy_buffer_encoder.c
             src/liblzma/common/easy_decoder_memusage.c
             src/liblzma/common/easy_encoder.c
             src/liblzma/common/easy_encoder_memusage.c
             src/liblzma/common/easy_preset.c
             src/liblzma/common/filter_buffer_decoder.c
             src/liblzma/common/filter_buffer_encoder.c
             src/liblzma/common/filter_common.c
             src/liblzma/common/filter_decoder.c
             src/liblzma/common/filter_encoder.c
             src/liblzma/common/filter_flags_decoder.c
             src/liblzma/common/filter_flags_encoder.c
             src/liblzma/common/hardware_cputhreads.c
             src/liblzma/common/hardware_physmem.c
             src/liblzma/common/index.c
             src/liblzma/common/index_decoder.c
             src/liblzma/common/index_encoder.c
             src/liblzma/common/index_hash.c
             src/liblzma/common/outqueue.c
             src/liblzma/common/stream_buffer_decoder.c
             src/liblzma/common/stream_buffer_encoder.c
             src/liblzma/common/stream_decoder.c
             src/liblzma/common/stream_encoder.c
             src/liblzma/common/stream_encoder_mt.c
             src/liblzma/common/stream_flags_common.c
             src/liblzma/common/stream_flags_decoder.c
             src/liblzma/common/stream_flags_encoder.c
             src/liblzma/common/vli_decoder.c
             src/liblzma/common/vli_encoder.c
             src/liblzma/common/vli_size.c
             src/liblzma/delta/delta_common.c
             src/liblzma/delta/delta_decoder.c
             src/liblzma/delta/delta_encoder.c
             src/liblzma/lzma/fastpos_table.c
             src/liblzma/lzma/lzma2_decoder.c
             src/liblzma/lzma/lzma2_encoder.c
             src/liblzma/lzma/lzma_decoder.c
             src/liblzma/lzma/lzma_encoder.c
             src/liblzma/lzma/lzma_encoder_optimum_fast.c
             src/liblzma/lzma/lzma_encoder_optimum_normal.c
             src/liblzma/lzma/lzma_encoder_presets.c
             src/liblzma/lz/lz_decoder.c
             src/liblzma/lz/lz_encoder.c
             src/liblzma/lz/lz_encoder_mf.c
             src/liblzma/rangecoder/price_table.c
             src/liblzma/simple/arm.c
             src/liblzma/simple/armthumb.c
             src/liblzma/simple/ia64.c
             src/liblzma/simple/powerpc.c
             src/liblzma/simple/simple_coder.c
             src/liblzma/simple/simple_decoder.c
             src/liblzma/simple/simple_encoder.c
             src/liblzma/simple/sparc.c
             src/liblzma/simple/x86.c)

set (HEADERS src/common/mythread.h
             src/common/sysdefs.h
             src/common/tuklib_common.h
             src/common/tuklib_config.h
             src/common/tuklib_cpucores.h
             src/common/tuklib_integer.h
             src/common/tuklib_physmem.h
             src/liblzma/api/lzma.h
             src/liblzma/api/lzma/base.h
             src/liblzma/api/lzma/bcj.h
             src/liblzma/api/lzma/block.h
             src/liblzma/api/lzma/check.h
             src/liblzma/api/lzma/container.h
             src/liblzma/api/lzma/delta.h
             src/liblzma/api/lzma/filter.h
             src/liblzma/api/lzma/hardware.h
             src/liblzma/api/lzma/index.h
             src/liblzma/api/lzma/index_hash.h
             src/liblzma/api/lzma/lzma12.h
             src/liblzma/api/lzma/stream_flags.h
             src/liblzma/api/lzma/version.h
             src/liblzma/api/lzma/vli.h
             src/liblzma/check/check.h
             src/liblzma/check/crc32_table_be.h
             src/liblzma/check/crc32_table_le.h
             src/liblzma/check/crc64_table_be.h
             src/liblzma/check/crc64_table_le.h
             src/liblzma/check/crc_macros.h
             src/liblzma/common/alone_decoder.h
             src/liblzma/common/block_buffer_encoder.h
             src/liblzma/common/block_decoder.h
             src/liblzma/common/block_encoder.h
             src/liblzma/common/common.h
             src/liblzma/common/easy_preset.h
             src/liblzma/common/filter_common.h
             src/liblzma/common/filter_decoder.h
             src/liblzma/common/filter_encoder.h
             src/liblzma/common/index.h
             src/liblzma/common/index_encoder.h
             src/liblzma/common/memcmplen.h
             src/liblzma/common/outqueue.h
             src/liblzma/common/stream_decoder.h
             src/liblzma/common/stream_flags_common.h
             src/liblzma/delta/delta_common.h
             src/liblzma/delta/delta_decoder.h
             src/liblzma/delta/delta_encoder.h
             src/liblzma/delta/delta_private.h
             src/liblzma/lzma/fastpos.h
             src/liblzma/lzma/lzma2_decoder.h
             src/liblzma/lzma/lzma2_encoder.h
             src/liblzma/lzma/lzma_common.h
             src/liblzma/lzma/lzma_decoder.h
             src/liblzma/lzma/lzma_encoder.h
             src/liblzma/lzma/lzma_encoder_private.h
             src/liblzma/lz/lz_decoder.h
             src/liblzma/lz/lz_encoder.h
             src/liblzma/lz/lz_encoder_hash.h
             src/liblzma/lz/lz_encoder_hash_table.h
             src/liblzma/rangecoder/price.h
             src/liblzma/rangecoder/range_common.h
             src/liblzma/rangecoder/range_decoder.h
             src/liblzma/rangecoder/range_encoder.h
             src/liblzma/simple/simple_coder.h
             src/liblzma/simple/simple_decoder.h
             src/liblzma/simple/simple_encoder.h
             src/liblzma/simple/simple_private.h)

include_directories(${CMAKE_CURRENT_SOURCE_DIR}/windows
                    ${CMAKE_CURRENT_SOURCE_DIR}/src/liblzma/common
                    ${CMAKE_CURRENT_SOURCE_DIR}/src/common
                    ${CMAKE_CURRENT_SOURCE_DIR}/src/liblzma/api
                    ${CMAKE_CURRENT_SOURCE_DIR}/src/liblzma/check
                    ${CMAKE_CURRENT_SOURCE_DIR}/src/liblzma/delta
                    ${CMAKE_CURRENT_SOURCE_DIR}/src/liblzma/lz
                    ${CMAKE_CURRENT_SOURCE_DIR}/src/liblzma/lzma
                    ${CMAKE_CURRENT_SOURCE_DIR}/src/liblzma/rangecoder
                    ${CMAKE_CURRENT_SOURCE_DIR}/src/liblzma/simple)

add_library(xz SHARED ${SOURCES} ${HEADERS})
set_target_properties(xz PROPERTIES OUTPUT_NAME "xz")

install(TARGETS xz
        LIBRARY DESTINATION lib
        RUNTIME DESTINATION bin)