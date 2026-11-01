/* TitanDefender minifilter skeleton (Windows) */
#include <fltKernel.h>
#include <dontuse.h>
#include <suppress.h>

PFLT_FILTER gFilterHandle = NULL;

NTSTATUS FLTAPI TitanUnload(FLT_FILTER_UNLOAD_FLAGS Flags) {
    UNREFERENCED_PARAMETER(Flags);
    FltUnregisterFilter(gFilterHandle);
    return STATUS_SUCCESS;
}

NTSTATUS DriverEntry(PDRIVER_OBJECT DriverObject, PUNICODE_STRING RegistryPath) {
    UNREFERENCED_PARAMETER(RegistryPath);
    NTSTATUS status = FltRegisterFilter(DriverObject, &FilterRegistration, &gFilterHandle);
    if (NT_SUCCESS(status)) {
        status = FltStartFiltering(gFilterHandle);
    }
    if (!NT_SUCCESS(status)) {
        if (gFilterHandle) FltUnregisterFilter(gFilterHandle);
    }
    return status;
}
