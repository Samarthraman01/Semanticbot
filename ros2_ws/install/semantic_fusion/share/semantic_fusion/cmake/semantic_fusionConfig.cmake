# generated from ament/cmake/core/templates/nameConfig.cmake.in

# prevent multiple inclusion
if(_semantic_fusion_CONFIG_INCLUDED)
  # ensure to keep the found flag the same
  if(NOT DEFINED semantic_fusion_FOUND)
    # explicitly set it to FALSE, otherwise CMake will set it to TRUE
    set(semantic_fusion_FOUND FALSE)
  elseif(NOT semantic_fusion_FOUND)
    # use separate condition to avoid uninitialized variable warning
    set(semantic_fusion_FOUND FALSE)
  endif()
  return()
endif()
set(_semantic_fusion_CONFIG_INCLUDED TRUE)

# output package information
if(NOT semantic_fusion_FIND_QUIETLY)
  message(STATUS "Found semantic_fusion: 0.0.0 (${semantic_fusion_DIR})")
endif()

# warn when using a deprecated package
if(NOT "" STREQUAL "")
  set(_msg "Package 'semantic_fusion' is deprecated")
  # append custom deprecation text if available
  if(NOT "" STREQUAL "TRUE")
    set(_msg "${_msg} ()")
  endif()
  # optionally quiet the deprecation message
  if(NOT ${semantic_fusion_DEPRECATED_QUIET})
    message(DEPRECATION "${_msg}")
  endif()
endif()

# flag package as ament-based to distinguish it after being find_package()-ed
set(semantic_fusion_FOUND_AMENT_PACKAGE TRUE)

# include all config extra files
set(_extras "")
foreach(_extra ${_extras})
  include("${semantic_fusion_DIR}/${_extra}")
endforeach()
