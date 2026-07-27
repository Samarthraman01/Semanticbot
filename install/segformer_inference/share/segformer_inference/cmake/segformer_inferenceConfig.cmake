# generated from ament/cmake/core/templates/nameConfig.cmake.in

# prevent multiple inclusion
if(_segformer_inference_CONFIG_INCLUDED)
  # ensure to keep the found flag the same
  if(NOT DEFINED segformer_inference_FOUND)
    # explicitly set it to FALSE, otherwise CMake will set it to TRUE
    set(segformer_inference_FOUND FALSE)
  elseif(NOT segformer_inference_FOUND)
    # use separate condition to avoid uninitialized variable warning
    set(segformer_inference_FOUND FALSE)
  endif()
  return()
endif()
set(_segformer_inference_CONFIG_INCLUDED TRUE)

# output package information
if(NOT segformer_inference_FIND_QUIETLY)
  message(STATUS "Found segformer_inference: 0.0.0 (${segformer_inference_DIR})")
endif()

# warn when using a deprecated package
if(NOT "" STREQUAL "")
  set(_msg "Package 'segformer_inference' is deprecated")
  # append custom deprecation text if available
  if(NOT "" STREQUAL "TRUE")
    set(_msg "${_msg} ()")
  endif()
  # optionally quiet the deprecation message
  if(NOT ${segformer_inference_DEPRECATED_QUIET})
    message(DEPRECATION "${_msg}")
  endif()
endif()

# flag package as ament-based to distinguish it after being find_package()-ed
set(segformer_inference_FOUND_AMENT_PACKAGE TRUE)

# include all config extra files
set(_extras "")
foreach(_extra ${_extras})
  include("${segformer_inference_DIR}/${_extra}")
endforeach()
