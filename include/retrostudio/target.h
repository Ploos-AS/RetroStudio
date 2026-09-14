#ifndef RETROSTUDIO_TARGET_H
#define RETROSTUDIO_TARGET_H

#ifdef __cplusplus
extern "C" {
#endif

#define RETROSTUDIO_TARGET_API_VERSION 1u

typedef enum RetroStudioDiagnosticLevel {
    RETROSTUDIO_DIAGNOSTIC_INFO = 0,
    RETROSTUDIO_DIAGNOSTIC_WARNING = 1,
    RETROSTUDIO_DIAGNOSTIC_ERROR = 2
} RetroStudioDiagnosticLevel;

typedef struct RetroStudioTargetDescriptor {
    unsigned int api_version;
    const char *id;
    const char *display_name;
    const char *backend_version;
} RetroStudioTargetDescriptor;

/*
 * M0 contract only. Production lifecycle/build hooks are introduced in M2.
 * Keeping this deliberately small prevents the first backend from defining
 * assumptions that all later machines would have to inherit.
 */
typedef const RetroStudioTargetDescriptor *(*RetroStudioDescribeTargetFn)(void);

#ifdef __cplusplus
}
#endif

#endif
