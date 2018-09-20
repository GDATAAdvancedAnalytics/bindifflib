cmake_minimum_required(VERSION 2.7)

project(libtiff)

Find_Package(zlib)
Find_Package(jpeg)

set (SOURCES port/strcasecmp.c port/getopt.c 
    libtiff/tif_aux.c libtiff/tif_close.c libtiff/tif_codec.c 
    libtiff/tif_color.c libtiff/tif_compress.c libtiff/tif_dir.c 
    libtiff/tif_dirinfo.c libtiff/tif_dirread.c libtiff/tif_dirwrite.c 
    libtiff/tif_dumpmode.c libtiff/tif_error.c libtiff/tif_extension.c 
    libtiff/tif_fax3.c libtiff/tif_fax3sm.c libtiff/tif_getimage.c 
    libtiff/tif_jpeg.c libtiff/tif_ojpeg.c libtiff/tif_flush.c 
    libtiff/tif_luv.c libtiff/tif_lzw.c libtiff/tif_next.c 
    libtiff/tif_open.c libtiff/tif_packbits.c libtiff/tif_pixarlog.c 
    libtiff/tif_predict.c libtiff/tif_print.c libtiff/tif_read.c 
    libtiff/tif_stream.cxx libtiff/tif_swab.c libtiff/tif_strip.c 
    libtiff/tif_thunder.c libtiff/tif_tile.c libtiff/tif_version.c 
    libtiff/tif_warning.c libtiff/tif_write.c libtiff/tif_zip.c libtiff/tif_win32.c)

if (NOT (EXISTS ${CMAKE_CURRENT_SOURCE_DIR}/libtiff/tif_config.h))
    file(RENAME libtiff/tif_config.h.vc libtiff/tif_config.h)
endif()
if (NOT (EXISTS ${CMAKE_CURRENT_SOURCE_DIR}/libtiff/tiffconf.h))
    file(RENAME libtiff/tiffconf.h.vc libtiff/tiffconf.h)
endif()

file(GLOB HEADERS port/*.h libtiff/*.h)

add_library(libtiff SHARED ${SOURCES} ${HEADERS})

add_definitions(-DUSE_WIN32_FILEIO)

set_target_properties(libtiff PROPERTIES OUTPUT_NAME "libtiff")
set_target_properties(libtiff PROPERTIES LINK_FLAGS "/def:\"${CMAKE_CURRENT_SOURCE_DIR}/libtiff/libtiff.def\"")

include_directories(libtiff ${JPEG_INCLUDE_DIR} ${ZLIB_INCLUDE_DIR})
target_link_libraries(libtiff ${JPEG_LIBRARY} ${ZLIB_LIBRARIES})

install(TARGETS libtiff 
        LIBRARY DESTINATION lib
        RUNTIME DESTINATION bin)

install(FILES ${HEADERS} DESTINATION include)