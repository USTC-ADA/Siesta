/* -*- C -*-

   mpiP MPI Profiler ( http://llnl.github.io/mpiP )

   Please see COPYRIGHT AND LICENSE information at the end of this file.

   -----

   wrappers_special.c -- wrappers that demand special attention

 */

#ifndef lint
static char *svnid = "$Id$";
#endif

#include "mpiPconfig.h"
#include "mpiPi.h"
#include "symbols.h"
#ifdef ENABLE_FORTRAN_WEAK_SYMS
#include "weak-symbols-special.h"
#endif
#include "papi.h"
#include "papi_utils.h"
#include <string.h>
#define mpiPi_GETTIMEDIFF(end, start) ((*end) - (*start))
#define mpiPi_GETTIME(timeaddr) (*(timeaddr) = (PMPI_Wtime()*USECS))
/* ----- INIT -------------------------------------------------- */

extern long long **values;
extern int EnventSet;
extern int event_count;

static int _MPI_Init(int *argc, char ***argv) {
    int rc = 0;
    int enabledStatus;
    char event_buffer[128];
    double start_from_begin, end_from_begin;
    mpiPi_TIME start, end, end2;

    enabledStatus = mpiPi.enabled;
    mpiPi.enabled = 0;
    
    mpiPi_GETTIME(&start);


    rc = PMPI_Init(argc, argv);

    mpiPi.enabled = enabledStatus;

#if defined(Linux) && !defined(ppc64)
    mpiPi.appFullName = getProcExeLink();
    mpiPi_msg_debug("appFullName is %s\n", mpiPi.appFullName);
    mpiPi_init(GetBaseAppName(mpiPi.appFullName), MPIPI_MODE_ST);
#else
    if (argv != NULL && *argv != NULL && **argv != NULL) {
        mpiPi_init(GetBaseAppName(**argv), MPIPI_MODE_ST);
        mpiPi.appFullName = strdup(**argv);
    } else {
        mpiPi_init("Unknown", MPIPI_MODE_ST);
        mpiPi_msg_debug("argv is NULL\n");
    }
#endif
    mpiPi_GETTIME(&end);
    start_from_begin = mpiPi_GETTIMEDIFF(&start, &mpiPi.time_begin);
    end_from_begin = mpiPi_GETTIMEDIFF(&end, &mpiPi.time_begin);

    sprintf(event_buffer, "%d,MPI_Init,%d;%d;%d,%.0lf,%.0lf,%d:\n", mpiPi.rank,
            0, 0, 0, start_from_begin, end_from_begin, -1);
    list_push(&mpiPi.event_list, event_buffer);

    int papi_retval, num_tests = 1, num_events = 0, i = 0;
    char **papi_events;
    papi_retval = PAPI_library_init(PAPI_VER_CURRENT);
    if (papi_retval != PAPI_VER_CURRENT) {
        printf("PAPI_library_init Failed! retval = %d\n", papi_retval);
    }
    // papi_retval = PAPI_multiplex_init();
    // if (papi_retval != PAPI_OK)
    //     printf("PAPI_multiplex_init Failed! retval = %d\n", papi_retval);

    papi_retval = PAPI_create_eventset(&EventSet);
    if (papi_retval != PAPI_OK) {
        printf("PAPI_create_eventset Failed!\n");
    }
    papi_retval = PAPI_assign_eventset_component(EventSet, 0);
    if (papi_retval != PAPI_OK)
        printf("PAPI_assign_eventset_component Failed!, retval is %d\n",
               papi_retval);

    // papi_retval = PAPI_set_multiplex(EventSet);
    // if (papi_retval != PAPI_OK)
    //     printf("PAPI_set_multiplex Failed! retval = %d\n", papi_retval);

    papi_events = read_PAPIEvents_from_environment_variables(&num_events);
    event_count = num_events;
    // printf("event_count=%d\n", event_count);
    for (i = 0; i < num_events; i++) {
        // printf("add_event %s\n", papi_events[i]);
        papi_retval = PAPI_add_named_event(EventSet, papi_events[i]);
        if (papi_retval != PAPI_OK) {
            printf("PAPI_add_named_event Failed! Event is %s, retval is %d\n",
                   papi_events[i], papi_retval);
        }
    }
    values = allocate_values_space(num_tests, num_events);

    papi_retval = PAPI_start(EventSet);
    if (papi_retval != PAPI_OK) {
        printf("PAPI_start Failed! retval = %d, rank=%d\n", papi_retval,
               mpiPi.rank);
    }
    papi_retval = PAPI_read(EventSet, values[0]);
    if (papi_retval != PAPI_OK) {
        printf("PAPI_read Failed!");
    }
    papi_retval = PAPI_reset(EventSet);
    if (papi_retval != PAPI_OK) {
        printf("PAPI_reset Failed! retval = %d, rank=%d\n", papi_retval,
               mpiPi.rank);
    }
    // mpiPi_GETTIME (&mpiPi.time_begin);
    return rc;
}

extern int MPI_Init(int *argc, char ***argv) {
    // printf("in mpi init\n");
    int rc = 0;

    mpiPi.toolname = "mpiP";

    rc = _MPI_Init(argc, argv);

    if (argc != NULL && argv != NULL)
        mpiPi_copy_given_args(&(mpiPi.ac), mpiPi.av, MPIP_COPIED_ARGS_MAX,
                              *argc, *argv);
    else {
#ifdef Linux
        getProcCmdLine(&(mpiPi.ac), mpiPi.av);
#else
        mpiPi.ac = 0;
#endif
    }

    return rc;
}

extern void F77_MPI_INIT(int *ierr) {
    int rc = 0;
    char **tmp_argv;
    // printf("int fortran mpiinit\n");
    mpiPi.toolname = "mpiP";
#ifdef Linux
    getProcCmdLine(&(mpiPi.ac), mpiPi.av);
#else
    mpiPi_copy_args(&(mpiPi.ac), mpiPi.av, MPIP_COPIED_ARGS_MAX);
#endif

    tmp_argv = mpiPi.av;
    rc = _MPI_Init(&(mpiPi.ac), (char ***)&tmp_argv);
    *ierr = rc;

    return;
}

/* ----- INIT_thread -------------------------------------------------- */

static int _MPI_Init_thread(int *argc, char ***argv, int required,
                            int *provided) {
    // printf("in mpi init_thread\n");
    int rc = 0;
    int enabledStatus;
    mpiPi_thr_mode_t mode = MPIPI_MODE_ST;

    enabledStatus = mpiPi.enabled;
    mpiPi.enabled = 0;

    rc = PMPI_Init_thread(argc, argv, required, provided);
    if (MPI_THREAD_MULTIPLE == *provided) {
        mode = MPIPI_MODE_MT;
    }

    mpiPi.enabled = enabledStatus;

#if defined(Linux) && !defined(ppc64)
    mpiPi.appFullName = getProcExeLink();
    mpiPi_msg_debug("appFullName is %s\n", mpiPi.appFullName);
    mpiPi_init(GetBaseAppName(mpiPi.appFullName), mode);
#else
    if (argv != NULL && *argv != NULL && **argv != NULL) {
        mpiPi_init(GetBaseAppName(**argv), mode);
        mpiPi.appFullName = strdup(**argv);
    } else {
        mpiPi_init("Unknown", MPIPI_MODE_MT);
        mpiPi_msg_debug("argv is NULL\n");
    }
#endif

    // printf("in mpi init_thread\n");
    int papi_retval, num_tests = 1, num_events = 0, i = 0;
    char **papi_events;
    // char event_name1[]="PAPI_TOT_CYC";
    // char event_name2[]="PAPI_TOT_INS";
    papi_retval = PAPI_library_init(PAPI_VER_CURRENT);
    if (papi_retval != PAPI_VER_CURRENT) {
        printf("PAPI_library_init Failed! retval = %d\n", papi_retval);
    }
    // papi_retval = PAPI_multiplex_init();
    // if (papi_retval != PAPI_OK)
    //     printf("PAPI_multiplex_init Failed! retval = %d\n", papi_retval);

    papi_retval = PAPI_create_eventset(&EventSet);
    if (papi_retval != PAPI_OK) {
        printf("PAPI_create_eventset Failed!\n");
    }
    papi_retval = PAPI_assign_eventset_component(EventSet, 0);
    if (papi_retval != PAPI_OK)
        printf("PAPI_assign_eventset_component Failed!, retval is %d\n",
               papi_retval);

    // papi_retval = PAPI_set_multiplex(EventSet);
    // if (papi_retval != PAPI_OK)
    //     printf("PAPI_set_multiplex Failed! retval = %d\n", papi_retval);
    papi_events = read_PAPIEvents_from_environment_variables(&num_events);
    event_count = num_events;
    printf("event_count=%d\n", event_count);
    for (i = 0; i < num_events; i++) {
        printf("add_event %s\n", papi_events[i]);
        papi_retval = PAPI_add_named_event(EventSet, papi_events[i]);
        if (papi_retval != PAPI_OK) {
            printf("PAPI_add_named_event Failed! Event is %s, retval is %d\n",
                   papi_events[i], papi_retval);
        }
    }
    values = allocate_values_space(num_tests, num_events);

    papi_retval = PAPI_start(EventSet);
    if (papi_retval != PAPI_OK) {
        printf("PAPI_start Failed! retval = %d, rank=%d\n", papi_retval,
               mpiPi.rank);
    }
    papi_retval = PAPI_read(EventSet, values[0]);
    if (papi_retval != PAPI_OK) {
        printf("PAPI_read Failed!");
    }
    papi_retval = PAPI_reset(EventSet);
    if (papi_retval != PAPI_OK) {
        printf("PAPI_reset Failed! retval = %d, rank=%d\n", papi_retval,
               mpiPi.rank);
    }

    return rc;
}

extern int MPI_Init_thread(int *argc, char ***argv, int required,
                           int *provided) {
    int rc = 0;

    mpiPi.toolname = "mpiP";

    rc = _MPI_Init_thread(argc, argv, required, provided);

    if (argc != NULL && argv != NULL)
        mpiPi_copy_given_args(&(mpiPi.ac), mpiPi.av, MPIP_COPIED_ARGS_MAX,
                              *argc, *argv);
    else {
#ifdef Linux
        getProcCmdLine(&(mpiPi.ac), mpiPi.av);
#else
        mpiPi.ac = 0;
#endif
    }

    return rc;
}

extern void F77_MPI_INIT_THREAD(int *required, int *provided, int *ierr) {
    int rc = 0;
    char **tmp_argv;

    mpiPi.toolname = "mpiP";
#ifdef Linux
    getProcCmdLine(&(mpiPi.ac), mpiPi.av);
#else
    mpiPi_copy_args(&(mpiPi.ac), mpiPi.av, MPIP_COPIED_ARGS_MAX);
#endif

    tmp_argv = mpiPi.av;
    rc =
        _MPI_Init_thread(&(mpiPi.ac), (char ***)&tmp_argv, *required, provided);
    *ierr = rc;

    return;
}

/* ----- FINALIZE -------------------------------------------------- */

static int _MPI_Finalize() {
  char event_buffer[128];
    double start_from_begin, end_from_begin;
    mpiPi_TIME start, end, end2;

    int papi_retval;
    papi_retval = PAPI_read(EventSet, values[0]);
    if (papi_retval != PAPI_OK) {
        printf("PAPI_read Failed!");
    }
    sprintf(event_buffer, "%d, MPI_Compute,", mpiPi.rank);
    int papi_it = 0;
    for (papi_it = 0; papi_it < event_count; papi_it++) {
        sprintf(event_buffer + strlen(event_buffer), "%lld;",
                values[0][papi_it]);
    }
    sprintf(event_buffer + strlen(event_buffer), "\n");
    list_push(&mpiPi.event_list, event_buffer);
    
    int rc = 0;
    mpiPi_GETTIME(&start);
    mpiPi_finalize();
     mpiPi_GETTIME(&end);
    start_from_begin = mpiPi_GETTIMEDIFF(&start, &mpiPi.time_begin);
    end_from_begin = mpiPi_GETTIMEDIFF(&end, &mpiPi.time_begin);

    sprintf(event_buffer, "%d,MPI_Init,%d;%d;%d,%.0lf,%.0lf,%p\n", mpiPi.rank,
            0, 0, 0, start_from_begin, end_from_begin, 0);
    list_push(&mpiPi.event_list, event_buffer);

    mpiPi.enabled = 0;
    mpiPi_msg_debug("calling PMPI_Finalize\n");
    rc = PMPI_Finalize();
    mpiPi_msg_debug("returning from PMPI_Finalize\n");

    return rc;
}

extern int MPI_Finalize(void) {
    int rc = 0;

    rc = _MPI_Finalize();

    return rc;
}

extern void F77_MPI_FINALIZE(int *ierr) {
    int rc = 0;

    rc = _MPI_Finalize();
    *ierr = rc;

    return;
}

/*

<license>

Copyright (c) 2006, The Regents of the University of California.
Produced at the Lawrence Livermore National Laboratory
Written by Jeffery Vetter and Christopher Chambreau.
UCRL-CODE-223450.
All rights reserved.

This file is part of mpiP.  For details, see http://llnl.github.io/mpiP.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:

* Redistributions of source code must retain the above copyright
notice, this list of conditions and the disclaimer below.

* Redistributions in binary form must reproduce the above copyright
notice, this list of conditions and the disclaimer (as noted below) in
the documentation and/or other materials provided with the
distribution.

* Neither the name of the UC/LLNL nor the names of its contributors
may be used to endorse or promote products derived from this software
without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE REGENTS OF
THE UNIVERSITY OF CALIFORNIA, THE U.S. DEPARTMENT OF ENERGY OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


Additional BSD Notice

1. This notice is required to be provided under our contract with the
U.S. Department of Energy (DOE).  This work was produced at the
University of California, Lawrence Livermore National Laboratory under
Contract No. W-7405-ENG-48 with the DOE.

2. Neither the United States Government nor the University of
California nor any of their employees, makes any warranty, express or
implied, or assumes any liability or responsibility for the accuracy,
completeness, or usefulness of any information, apparatus, product, or
process disclosed, or represents that its use would not infringe
privately-owned rights.

3.  Also, reference herein to any specific commercial products,
process, or services by trade name, trademark, manufacturer or
otherwise does not necessarily constitute or imply its endorsement,
recommendation, or favoring by the United States Government or the
University of California.  The views and opinions of authors expressed
herein do not necessarily state or reflect those of the United States
Government or the University of California, and shall not be used for
advertising or product endorsement purposes.

</license>

*/

/* eof */
