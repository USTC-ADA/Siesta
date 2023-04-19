/* mpiPconfig.h.  Generated from mpiPconfig.h.in by configure.  */
/* mpiPconfig.h.in.  Generated from configure.ac by autoheader.  */

/* "Use collective reporting by default" */
/* #undef COLLECTIVE_REPORT_DEFAULT */

/* The default format of the report */
#define DEFAULT_REPORT_FORMAT mpiPi_style_verbose

/* "Only build API" */
/* #undef ENABLE_API_ONLY */

/* Enable BFD library for the PC to source lookups */
/* #undef ENABLE_BFD */

/* Enable weak symbols for FORTRAN */
/* #undef ENABLE_FORTRAN_WEAK_SYMS */

/* F77 symbols */
#define F77_SYMBOLS symbol_

/* ARM LSE */
/* #undef HAVE_ARM_LSE */

/* BFD booleans */
/* #undef HAVE_BFD_BOOLEAN */

/* BFD get section size */
/* #undef HAVE_BFD_GET_SECTION_SIZE */

/* BFD macros available before version 2.34 */
/* #undef HAVE_BFD_GET_SECTION_MACROS */

/* Have demangling */
/* #undef HAVE_DEMANGLE_H */

/* Define to 1 if you have the <inttypes.h> header file. */
#define HAVE_INTTYPES_H 1

/* Define to 1 if you have the `m' library (-lm). */
#define HAVE_LIBM 1

/* Have libunwind */
#define HAVE_LIBUNWIND 1

/* Define to 1 if you have the <memory.h> header file. */
#define HAVE_MEMORY_H 1

/* Have MPIR to pointer */
/* #undef HAVE_MPIR_TOPOINTER */

/* Have MPI-IO */
#define HAVE_MPI_IO 1

/* Have MPI non-blocking collectives */
#define HAVE_MPI_NONBLOCKINGCOLLECTIVES 1

/* Have MPI RMA */
#define HAVE_MPI_RMA 1

/* Define to 1 if you have the <stdint.h> header file. */
#define HAVE_STDINT_H 1

/* Define to 1 if you have the <stdlib.h> header file. */
#define HAVE_STDLIB_H 1

/* Define to 1 if you have the <strings.h> header file. */
#define HAVE_STRINGS_H 1

/* Define to 1 if you have the <string.h> header file. */
#define HAVE_STRING_H 1

/* Define to 1 if you have the <sys/stat.h> header file. */
#define HAVE_SYS_STAT_H 1

/* Define to 1 if you have the <sys/types.h> header file. */
#define HAVE_SYS_TYPES_H 1

/* Define to 1 if you have the <unistd.h> header file. */
#define HAVE_UNISTD_H 1

/* Stack depth of callsites in report */
#define MPIP_CALLSITE_REPORT_STACK_DEPTH_MAX 8

/* Internal stack frames */
#define MPIP_INTERNAL_STACK_DEPTH 3

/* Recorded stack depth of callsites */
#define MPIP_CALLSITE_STACK_DEPTH_MAX (MPIP_CALLSITE_REPORT_STACK_DEPTH_MAX + MPIP_INTERNAL_STACK_DEPTH)

/* MPI check time */
/* #undef MPIP_CHECK_TIME */

/* Maximum number of command line arguments copied */
#define MPIP_COPIED_ARGS_MAX 32

/* Need Real-time declaration */
/* #undef NEED_MREAD_REAL_TIME_DECL */

/* Define to the address where bug reports for this package should be sent. */
#define PACKAGE_BUGREPORT ""

/* Define to the full name of this package. */
#define PACKAGE_NAME "mpiP"

/* Define to the full name and version of this package. */
#define PACKAGE_STRING "mpiP 3.5"

/* Define to the one symbol short name of this package. */
#define PACKAGE_TARNAME "mpip"

/* Define to the home page for this package. */
#define PACKAGE_URL ""

/* Define to the version of this package. */
#define PACKAGE_VERSION "3.5"

/* The size of `void*', as computed by sizeof. */
#define SIZEOF_VOIDP 8

/* SO lookup */
/* #undef SO_LOOKUP */

/* Define to 1 if you have the ANSI C header files. */
#define STDC_HEADERS 1

/* Use backtrace */
/* #undef USE_BACKTRACE */

/* Use clock_gettime for timing */
/* #undef USE_CLOCK_GETTIME */

/* Use dlock */
/* #undef USE_DCLOCK */

/* Use getarg */
/* #undef USE_GETARG */

/* Use gettimofday */
/* #undef USE_GETTIMEOFDAY */

/* Use libdwarf */
/* #undef USE_LIBDWARF */

/* Use MPI v3 constructions */
#define USE_MPI3_CONSTS 1

/* Use read real time */
/* #undef USE_READ_REAL_TIME */

/* Use RTC */
/* #undef USE_RTC */

/* Use RTS get timebase */
/* #undef USE_RTS_GET_TIMEBASE */

/* Use setjmp */
/* #undef USE_SETJMP */

/* Use MPI_Wtime */
#define USE_WTIME 1
