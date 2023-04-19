/* -*- C -*-

   mpiP MPI Profiler ( http://llnl.github.io/mpiP )

   Please see COPYRIGHT AND LICENSE information at the end of this file.

   -----

   mpiPi.c -- main mpiP internal functions

 */

#ifndef lint
static char *svnid = "$Id$";
#endif

#include <string.h>
#include <float.h>
#include <unistd.h>
#include "mpiPi.h"



static int
mpiPi_callsite_stats_src_hashkey (const void *p)
{
  int res = 0;
  callsite_stats_t *csp = (callsite_stats_t *) p;
  MPIP_CALLSITE_STATS_COOKIE_ASSERT (csp);
  return 52271 ^ csp->op ^ res ^ csp->rank ^ csp->csid;
}

static int
mpiPi_callsite_stats_src_comparator (const void *p1, const void *p2)
{
  callsite_stats_t *csp_1 = (callsite_stats_t *) p1;
  callsite_stats_t *csp_2 = (callsite_stats_t *) p2;
  MPIP_CALLSITE_STATS_COOKIE_ASSERT (csp_1);
  MPIP_CALLSITE_STATS_COOKIE_ASSERT (csp_2);

#define express(f) {if ((csp_1->f) > (csp_2->f)) {return 1;} if ((csp_1->f) < (csp_2->f)) {return -1;}}
  express (op);
  express (csid);
  express (rank);
#undef express

  return 0;
}

static int
mpiPi_callsite_stats_src_id_hashkey (const void *p)
{
  int res = 0;
  callsite_stats_t *csp = (callsite_stats_t *) p;
  MPIP_CALLSITE_STATS_COOKIE_ASSERT (csp);
  return 52271 ^ csp->op ^ res ^ csp->csid;
}

static int
mpiPi_callsite_stats_src_id_comparator (const void *p1, const void *p2)
{
  callsite_stats_t *csp_1 = (callsite_stats_t *) p1;
  callsite_stats_t *csp_2 = (callsite_stats_t *) p2;
  MPIP_CALLSITE_STATS_COOKIE_ASSERT (csp_1);
  MPIP_CALLSITE_STATS_COOKIE_ASSERT (csp_2);

#define express(f) {if ((csp_1->f) > (csp_2->f)) {return 1;} if ((csp_1->f) < (csp_2->f)) {return -1;}}
  express (op);
  express (csid);
#undef express

  return 0;
}

#ifndef ENABLE_API_ONLY		/* { */
/* task level init
   - executed by each MPI task only once immediately after MPI_Init
*/

void DT_table_get(DT_table_t *DT_table, MPI_Datatype datatype, char *datatype_name)
{
  int i=0;
  //char test[32]="MPI_INT";
  //strcpy(datatype_name,test);
  //return test;
  for(i=0;i<DT_table->size;i++)
  {
    if(DT_table->items[i].datatype == (unsigned long long)datatype)
    {
      //printf("%d %d MPI_Datatype: %s\n",i, DT_table->size, DT_table->items[i].datatype_name);
      strcpy(datatype_name,DT_table->items[i].datatype_name);
      return;
    }
                
  }
  printf("DT_table error: undefined MPI_Datatype %llu\n",datatype);
}

void DT_table_init(DT_table_t *DT_table)
{
  int i = 0;
  memset(DT_table, 0, sizeof(DT_table_t));
  DT_table->items[i].datatype=(unsigned long long)MPI_LONG; strcpy(DT_table->items[i].datatype_name,"MPI_LONG"); i++;
  DT_table->items[i].datatype=(unsigned long long)MPI_INT; strcpy(DT_table->items[i].datatype_name,"MPI_INT"); i++;
  DT_table->items[i].datatype=(unsigned long long)MPI_DATATYPE_NULL; strcpy(DT_table->items[i].datatype_name,"MPI_DATATYPE_NULL"); i++;
  DT_table->items[i].datatype=(unsigned long long)MPI_CHAR; strcpy(DT_table->items[i].datatype_name,"MPI_CHAR"); i++;
  DT_table->items[i].datatype=(unsigned long long)MPI_LONG_LONG; strcpy(DT_table->items[i].datatype_name,"MPI_LONG_LONG"); i++;
  DT_table->items[i].datatype=(unsigned long long)MPI_FLOAT; strcpy(DT_table->items[i].datatype_name,"MPI_FLOAT"); i++;
  DT_table->items[i].datatype=(unsigned long long)MPI_DOUBLE; strcpy(DT_table->items[i].datatype_name,"MPI_DOUBLE"); i++;
  DT_table->items[i].datatype=(unsigned long long)MPI_UNSIGNED_CHAR; strcpy(DT_table->items[i].datatype_name,"MPI_UNSIGNED_CHAR"); i++;
  DT_table->items[i].datatype=(unsigned long long)MPI_SHORT; strcpy(DT_table->items[i].datatype_name,"MPI_SHORT"); i++;
  DT_table->items[i].datatype=(unsigned long long)MPI_UNSIGNED_SHORT; strcpy(DT_table->items[i].datatype_name,"MPI_UNSIGNED_SHORT"); i++;
  DT_table->items[i].datatype=(unsigned long long)MPI_UNSIGNED; strcpy(DT_table->items[i].datatype_name,"MPI_UNSIGNED"); i++;
  DT_table->items[i].datatype=(unsigned long long)MPI_UNSIGNED_LONG; strcpy(DT_table->items[i].datatype_name,"MPI_UNSIGNED_LONG"); i++;
  DT_table->items[i].datatype=(unsigned long long)MPI_LONG_LONG_INT; strcpy(DT_table->items[i].datatype_name,"MPI_LONG_LONG_INT"); i++;
  DT_table->items[i].datatype=(unsigned long long)MPI_LONG_DOUBLE; strcpy(DT_table->items[i].datatype_name,"MPI_LONG_DOUBLE"); i++;
  DT_table->items[i].datatype=(unsigned long long)MPI_BYTE; strcpy(DT_table->items[i].datatype_name,"MPI_BYTE"); i++;
  DT_table->items[i].datatype=(unsigned long long)MPI_WCHAR; strcpy(DT_table->items[i].datatype_name,"MPI_WCHAR"); i++;
  DT_table->items[i].datatype=(unsigned long long)MPI_PACKED; strcpy(DT_table->items[i].datatype_name,"MPI_PACKED"); i++;
  DT_table->items[i].datatype=(unsigned long long)MPI_C_COMPLEX; strcpy(DT_table->items[i].datatype_name,"MPI_C_COMPLEX"); i++;
  DT_table->items[i].datatype=(unsigned long long)MPI_C_FLOAT_COMPLEX; strcpy(DT_table->items[i].datatype_name,"MPI_C_FLOAT_COMPLEX"); i++;
  DT_table->items[i].datatype=(unsigned long long)MPI_C_DOUBLE_COMPLEX; strcpy(DT_table->items[i].datatype_name,"MPI_C_DOUBLE_COMPLEX"); i++;
  DT_table->items[i].datatype=(unsigned long long)MPI_C_LONG_DOUBLE_COMPLEX; strcpy(DT_table->items[i].datatype_name,"MPI_C_LONG_DOUBLE_COMPLEX"); i++;
  DT_table->items[i].datatype=(unsigned long long)MPI_2INT; strcpy(DT_table->items[i].datatype_name,"MPI_2INT"); i++;
  DT_table->items[i].datatype=(unsigned long long)MPI_C_BOOL; strcpy(DT_table->items[i].datatype_name,"MPI_C_BOOL"); i++;
  DT_table->items[i].datatype=(unsigned long long)MPI_SIGNED_CHAR; strcpy(DT_table->items[i].datatype_name,"MPI_SIGNED_CHAR"); i++;
  DT_table->items[i].datatype=(unsigned long long)MPI_UNSIGNED_LONG_LONG; strcpy(DT_table->items[i].datatype_name,"MPI_UNSIGNED_LONG_LONG"); i++;
  DT_table->items[i].datatype=(unsigned long long)MPI_CHARACTER; strcpy(DT_table->items[i].datatype_name,"MPI_CHARACTER"); i++;
  DT_table->items[i].datatype=(unsigned long long)MPI_INTEGER; strcpy(DT_table->items[i].datatype_name,"MPI_INTEGER"); i++;
  DT_table->items[i].datatype=(unsigned long long)MPI_REAL; strcpy(DT_table->items[i].datatype_name,"MPI_REAL"); i++;
  DT_table->items[i].datatype=(unsigned long long)MPI_LOGICAL; strcpy(DT_table->items[i].datatype_name,"MPI_LOGICAL"); i++;
  DT_table->items[i].datatype=(unsigned long long)MPI_COMPLEX; strcpy(DT_table->items[i].datatype_name,"MPI_COMPLEX"); i++;
  DT_table->items[i].datatype=(unsigned long long)MPI_DOUBLE_PRECISION; strcpy(DT_table->items[i].datatype_name,"MPI_DOUBLE_PRECISION"); i++;
  DT_table->items[i].datatype=(unsigned long long)MPI_INT8_T; strcpy(DT_table->items[i].datatype_name,"MPI_INT8_T"); i++;
  DT_table->items[i].datatype=(unsigned long long)MPI_INT16_T; strcpy(DT_table->items[i].datatype_name,"MPI_INT16_T"); i++;
  DT_table->items[i].datatype=(unsigned long long)MPI_INT32_T; strcpy(DT_table->items[i].datatype_name,"MPI_INT32_T"); i++;
  DT_table->items[i].datatype=(unsigned long long)MPI_INT64_T; strcpy(DT_table->items[i].datatype_name,"MPI_INT64_T"); i++;
  DT_table->items[i].datatype=(unsigned long long)MPI_UINT8_T; strcpy(DT_table->items[i].datatype_name,"MPI_UINT8_T"); i++;
  DT_table->items[i].datatype=(unsigned long long)MPI_UINT16_T; strcpy(DT_table->items[i].datatype_name,"MPI_UINT16_T"); i++;
  DT_table->items[i].datatype=(unsigned long long)MPI_UINT32_T; strcpy(DT_table->items[i].datatype_name,"MPI_UINT32_T"); i++;
  DT_table->items[i].datatype=(unsigned long long)MPI_UINT64_T; strcpy(DT_table->items[i].datatype_name,"MPI_UINT64_T"); i++;
  DT_table->items[i].datatype=(unsigned long long)MPI_AINT; strcpy(DT_table->items[i].datatype_name,"MPI_AINT"); i++;
  DT_table->items[i].datatype=(unsigned long long)MPI_OFFSET; strcpy(DT_table->items[i].datatype_name,"MPI_OFFSET"); i++;
  DT_table->items[i].datatype=(unsigned long long)MPI_FLOAT_INT; strcpy(DT_table->items[i].datatype_name,"MPI_FLOAT_INT"); i++;
  DT_table->items[i].datatype=(unsigned long long)MPI_DOUBLE_INT; strcpy(DT_table->items[i].datatype_name,"MPI_DOUBLE_INT"); i++;
  DT_table->items[i].datatype=(unsigned long long)MPI_LONG_INT; strcpy(DT_table->items[i].datatype_name,"MPI_LONG_INT"); i++;
  DT_table->items[i].datatype=(unsigned long long)MPI_SHORT_INT; strcpy(DT_table->items[i].datatype_name,"MPI_SHORT_INT"); i++;
  DT_table->items[i].datatype=(unsigned long long)MPI_LONG_DOUBLE_INT; strcpy(DT_table->items[i].datatype_name,"MPI_LONG_DOUBLE_INT"); i++;

  DT_table->size = i;
}

void
mpiPi_init (char *appName, mpiPi_thr_mode_t thr_mode)
{
  if (time (&mpiPi.start_timeofday) == (time_t) - 1)
    {
      mpiPi_msg_warn ("Could not get time of day from time()\n");
    }

  mpiPi.toolname = "mpiP";
  mpiPi.comm = MPI_COMM_WORLD;
  mpiPi.tag = 9821;
  mpiPi.procID = getpid ();
  mpiPi.appName = strdup (appName);
  PMPI_Comm_rank (mpiPi.comm, &mpiPi.rank);
  PMPI_Comm_size (mpiPi.comm, &mpiPi.size);
  PMPI_Get_processor_name (mpiPi.hostname, &mpiPi.hostnamelen);
  mpiPi.stdout_ = stdout;
  mpiPi.stderr_ = stderr;
  mpiPi.lookup = mpiPi_lookup;

  mpiPi.enabled = 1;
  mpiPi.enabledCount = 1;
  mpiPi.cumulativeTime = 0.0;
  mpiPi.global_app_time = 0.0;
  mpiPi.global_mpi_time = 0.0;
  mpiPi.global_mpi_size = 0.0;
  mpiPi.global_mpi_io = 0.0;
  mpiPi.global_mpi_rma = 0.0;
  mpiPi.global_mpi_msize_threshold_count = 0;
  mpiPi.global_mpi_sent_count = 0;
  mpiPi.global_time_callsite_count = 0;
  mpiPi.global_task_hostnames = NULL;
  mpiPi.global_task_app_time = NULL;
  mpiPi.global_task_mpi_time = NULL;

  list_init(&mpiPi.event_list);

  int i=0;
  DT_table_init(&mpiPi.DT_table);
  mpiPi_GETTIME (&mpiPi.time_begin);
  //for(i=0;i<mpiPi.DT_table.size;i++)
  //  printf("%s %s %llu\n",mpiPi.DT_table.items[i].datatype_name, DT_table_get(&mpiPi.DT_table,(MPI_Datatype)mpiPi.DT_table.items[i].datatype), mpiPi.DT_table.items[i].datatype);

  char tmpfilename[256];
  sprintf(tmpfilename,"%d.trace\0",mpiPi.rank);
  mpiPi.recfile = fopen(tmpfilename,"wb"); 
  printf("Open Rec File %s !\n", tmpfilename);
  /*if(mpiPi.rank==0)
  {
      printf("sizeof(MPI_Datatype): %d\n", sizeof(MPI_Datatype));
      printf("sizeof(MPI_Op): %d\n", sizeof(MPI_Op));
      printf("sizeof(MPI_Comm): %d\n", sizeof(MPI_Comm));
      printf("%s ", "MPI_DATATYPE_NULL");	printf("%llu\n",MPI_DATATYPE_NULL);
      printf("%s ", "MPI_CHAR");	printf("%llu\n",MPI_CHAR);
      printf("%s ", "MPI_UNSIGNED_CHAR");	printf("%llu\n",MPI_UNSIGNED_CHAR);
      printf("%s ", "MPI_SHORT");	printf("%llu\n",MPI_SHORT);
      printf("%s ", "MPI_UNSIGNED_SHORT");	printf("%llu\n",MPI_UNSIGNED_SHORT);
      printf("%s rank=%d ", "MPI_INT",mpiPi.rank);	printf("%llu\n",MPI_INT);
      printf("%s ", "MPI_UNSIGNED");	printf("%llu\n",MPI_UNSIGNED);
      printf("%s ", "MPI_LONG");	printf("%llu\n",MPI_LONG);
      printf("%s ", "MPI_UNSIGNED_LONG");	printf("%llu\n",MPI_UNSIGNED_LONG);
      printf("%s ", "MPI_LONG_LONG_INT");	printf("%llu\n",MPI_LONG_LONG_INT);
      printf("%s ", "MPI_LONG_LONG");	printf("%llu\n",MPI_LONG_LONG);
      printf("%s ", "MPI_FLOAT");	printf("%llu\n",MPI_FLOAT);
      printf("%s ", "MPI_DOUBLE");	printf("%llu\n",MPI_DOUBLE);
      printf("%s ", "MPI_LONG_DOUBLE");	printf("%llu\n",MPI_LONG_DOUBLE);
      printf("%s ", "MPI_BYTE");	printf("%llu\n",MPI_BYTE);
      printf("%s ", "MPI_WCHAR");	printf("%llu\n",MPI_WCHAR);
      printf("%s ", "MPI_PACKED");	printf("%llu\n",MPI_PACKED);
      printf("%s ", "MPI_C_COMPLEX");	printf("%llu\n",MPI_C_COMPLEX);
      printf("%s ", "MPI_C_FLOAT_COMPLEX");	printf("%llu\n",MPI_C_FLOAT_COMPLEX);
      printf("%s ", "MPI_C_DOUBLE_COMPLEX");	printf("%llu\n",MPI_C_DOUBLE_COMPLEX);
      printf("%s ", "MPI_C_LONG_DOUBLE_COMPLEX");	printf("%llu\n",MPI_C_LONG_DOUBLE_COMPLEX);
      printf("%s ", "MPI_2INT");	printf("%llu\n",MPI_2INT);
      printf("%s ", "MPI_C_BOOL");	printf("%llu\n",MPI_C_BOOL);
      printf("%s ", "MPI_SIGNED_CHAR");	printf("%llu\n",MPI_SIGNED_CHAR);
      printf("%s ", "MPI_UNSIGNED_LONG_LONG");	printf("%llu\n",MPI_UNSIGNED_LONG_LONG);
      printf("%s ", "MPI_CHARACTER");	printf("%llu\n",MPI_CHARACTER);
      printf("%s ", "MPI_INTEGER");	printf("%llu\n",MPI_INTEGER);
      printf("%s ", "MPI_REAL");	printf("%llu\n",MPI_REAL);
      printf("%s ", "MPI_LOGICAL");	printf("%llu\n",MPI_LOGICAL);
      printf("%s ", "MPI_COMPLEX");	printf("%llu\n",MPI_COMPLEX);
      printf("%s ", "MPI_DOUBLE_PRECISION");	printf("%llu\n",MPI_DOUBLE_PRECISION);
      printf("%s ", "MPI_INT8_T");	printf("%llu\n",MPI_INT8_T);
      printf("%s ", "MPI_INT16_T");	printf("%llu\n",MPI_INT16_T);
      printf("%s ", "MPI_INT32_T");	printf("%llu\n",MPI_INT32_T);
      printf("%s ", "MPI_INT64_T");	printf("%llu\n",MPI_INT64_T);
      printf("%s ", "MPI_UINT8_T");	printf("%llu\n",MPI_UINT8_T);
      printf("%s ", "MPI_UINT16_T");	printf("%llu\n",MPI_UINT16_T);
      printf("%s ", "MPI_UINT32_T");	printf("%llu\n",MPI_UINT32_T);
      printf("%s ", "MPI_UINT64_T");	printf("%llu\n",MPI_UINT64_T);
      printf("%s ", "MPI_AINT");	printf("%llu\n",MPI_AINT);
      printf("%s ", "MPI_OFFSET");	printf("%llu\n",MPI_OFFSET);
      printf("%s ", "MPI_FLOAT_INT");	printf("%llu\n",MPI_FLOAT_INT);
      printf("%s ", "MPI_DOUBLE_INT");	printf("%llu\n",MPI_DOUBLE_INT);
      printf("%s ", "MPI_LONG_INT");	printf("%llu\n",MPI_LONG_INT);
      printf("%s ", "MPI_SHORT_INT");	printf("%llu\n",MPI_SHORT_INT);
      printf("%s ", "MPI_LONG_DOUBLE_INT");	printf("%llu\n",MPI_LONG_DOUBLE_INT);
  }*/

  /* set some defaults values */
  mpiPi.collectorRank = 0;
  mpiPi.tableSize = 256;
  mpiPi.reportPrintThreshold = 0.0;
  mpiPi.baseNames = 0;
  mpiPi.reportFormat = MPIP_REPORT_SCI_FORMAT;
  mpiPi.calcCOV = 1;
  mpiPi.inAPIrtb = 0;
  mpiPi.do_lookup = 1;
  mpiPi.messageCountThreshold = -1;

  if (DEFAULT_REPORT_FORMAT == mpiPi_style_concise)
    {
      mpiPi.report_style = mpiPi_style_concise;
      mpiPi.reportStackDepth = 0;
      mpiPi.print_callsite_detail = 0;
    }
  else // verbose default
    {
      mpiPi.report_style = mpiPi_style_verbose;
      mpiPi.reportStackDepth = 1;
      mpiPi.print_callsite_detail = 1;
    }

  mpiPi.internalStackDepth = MPIP_INTERNAL_STACK_DEPTH;
  mpiPi.fullStackDepth = mpiPi.reportStackDepth + mpiPi.internalStackDepth;
  if ( mpiPi.fullStackDepth > MPIP_CALLSITE_STACK_DEPTH_MAX )
      mpiPi.fullStackDepth = MPIP_CALLSITE_STACK_DEPTH_MAX;

#ifdef COLLECTIVE_REPORT_DEFAULT
  mpiPi.collective_report = 1;
#else
  mpiPi.collective_report = 0;
#endif
  mpiPi.disable_finalize_report = 0;
  mpiPi.do_collective_stats_report = 0;
  mpiPi.do_pt2pt_stats_report = 0;
#ifdef SO_LOOKUP
  mpiPi.so_info = NULL;
#endif
  mpiPi_getenv ();

  mpiPi_stats_mt_init(&mpiPi.task_stats, thr_mode);

  /* -- welcome msg only collector  */
  if (mpiPi.collectorRank == mpiPi.rank)
    {
      mpiPi_msg ("%s V%d.%d.%d (Build %s/%s)\n", mpiPi.toolname, mpiPi_vmajor,
                 mpiPi_vminor, mpiPi_vpatch, mpiPi_vdate, mpiPi_vtime);
      mpiPi_msg ("\n");
    }

  mpiPi_msg_debug ("appName is %s\n", appName);
  mpiPi_msg_debug ("sizeof(callsite_stats_t) is %d\n",
                   sizeof (callsite_stats_t));
  mpiPi_msg_debug ("successful init on %d, %s\n", mpiPi.rank, mpiPi.hostname);


  if (mpiPi.enabled)
    {
      mpiPi_stats_mt_timer_start(&mpiPi.task_stats);
    }

  return;
}
#endif /* } ifndef ENABLE_API_ONLY */

static int
mpiPi_insert_callsite_records (callsite_stats_t * p)
{
  callsite_stats_t *csp = NULL;

  mpiPi_query_src (p);		/* sets the file/line in p */

  /* If exists, accumulate, otherwise insert. This is
     specifically for optimizations that have multiple PCs for
     one src line. We aggregate across rank after this.

     The collective_report reporting approach does not aggregate individual
     process callsite information at the collector process.
   */
  if (mpiPi.collective_report == 0)
    {
      if (NULL == h_search (mpiPi.global_callsite_stats, p, (void **) &csp))
        {
          callsite_stats_t *newp = NULL;
          newp = (callsite_stats_t *) malloc (sizeof (callsite_stats_t));

          memcpy (newp, p, sizeof (callsite_stats_t));
          /* insert new record into global */
          h_insert (mpiPi.global_callsite_stats, newp);
        }
      else
        mpiPi_cs_merge(csp, p);
    }

  /* Collect aggregate callsite summary information indpendent of rank. */
  if (NULL == h_search (mpiPi.global_callsite_stats_agg, p, (void **) &csp))
    {
      callsite_stats_t *newp = NULL;
      newp = (callsite_stats_t *) malloc (sizeof (callsite_stats_t));

      memcpy (newp, p, sizeof (callsite_stats_t));
      newp->rank = -1;

      if (mpiPi.calcCOV)
        {
          newp->siteData = (double *) malloc (mpiPi.size * sizeof (double));
          newp->siteData[0] = p->cumulativeTime;
          newp->siteDataIdx = 1;
        }

      /* insert new record into global */
      h_insert (mpiPi.global_callsite_stats_agg, newp);
    }
  else
    {
      mpiPi_cs_merge(csp, p);

      if (mpiPi.calcCOV)
        {
          csp->siteData[csp->siteDataIdx] = p->cumulativeTime;
          csp->siteDataIdx += 1;
        }
    }

  /* Do global accumulation while we are iterating through individual callsites */
  mpiPi.global_task_mpi_time[p->rank] += p->cumulativeTime;

  mpiPi.global_mpi_time += p->cumulativeTime;
  assert (mpiPi.global_mpi_time >= 0);
  mpiPi.global_mpi_size += p->cumulativeDataSent;
  mpiPi.global_mpi_io += p->cumulativeIO;
  mpiPi.global_mpi_rma += p->cumulativeRMA;
  if (p->cumulativeTime > 0)
    mpiPi.global_time_callsite_count++;

  if (p->cumulativeDataSent > 0)
    {
      mpiPi.global_mpi_msize_threshold_count += p->arbitraryMessageCount;
      mpiPi.global_mpi_sent_count += p->count;
    }

  return 1;
}

static int
callsite_sort_by_MPI_op (const void *a, const void *b)
{
  callsite_stats_t **a1 = (callsite_stats_t **) a;
  callsite_stats_t **b1 = (callsite_stats_t **) b;

  /* NOTE: want descending sort, so compares are reveresed */
  if ((*a1)->op < (*b1)->op)
    {
      return 1;
    }
  if ((*a1)->op > (*b1)->op)
    {
      return -1;
    }
  return 0;
}


static int
mpiPi_callsite_stats_MPI_id_hashkey (const void *p)
{
  callsite_stats_t *csp = (callsite_stats_t *) p;
  MPIP_CALLSITE_STATS_COOKIE_ASSERT (csp);
  return 52271 ^ csp->op;
}

static int
mpiPi_callsite_stats_op_comparator (const void *p1, const void *p2)
{
  callsite_stats_t *csp_1 = (callsite_stats_t *) p1;
  callsite_stats_t *csp_2 = (callsite_stats_t *) p2;
  MPIP_CALLSITE_STATS_COOKIE_ASSERT (csp_1);
  MPIP_CALLSITE_STATS_COOKIE_ASSERT (csp_2);

#define express(f) {if ((csp_1->f) > (csp_2->f)) {return 1;} if ((csp_1->f) < (csp_2->f)) {return -1;}}
  express (op);
#undef express

  return 0;
}


/*  Aggregate individual MPI call data by iterating through call sites.  */
static int
mpiPi_insert_MPI_records ()
{
  callsite_stats_t *csp = NULL;
  int i, ac;
  callsite_stats_t **av;
  callsite_stats_t *p;

  if (mpiPi.rank == mpiPi.collectorRank)
    {
      /*  Open hash table for MPI call data.  */
      mpiPi.global_MPI_stats_agg = h_open (mpiPi.tableSize,
                                           mpiPi_callsite_stats_MPI_id_hashkey,
                                           mpiPi_callsite_stats_op_comparator);

      /*  Get individual call data.  */
      h_gather_data (mpiPi.global_callsite_stats_agg, &ac, (void ***) &av);

      /*  Sort by MPI op.  */
      qsort (av, ac, sizeof (void *), callsite_sort_by_MPI_op);

      /*  For each call site, add call site info to hash table entry for MPI op, independent of rank.  */
      for (i = 0; i < ac; i++)
        {
          p = av[i];

          /* Check if there is already an entry for the MPI op. */
          if (NULL ==
              h_search (mpiPi.global_MPI_stats_agg, p, (void **) &csp))
            {
              callsite_stats_t *newp = NULL;
              newp = (callsite_stats_t *) malloc (sizeof (callsite_stats_t));
              memcpy (newp, p, sizeof (callsite_stats_t));
              newp->rank = -1;
              newp->csid = p->op - mpiPi_BASE;

              /* insert new record into global */
              h_insert (mpiPi.global_MPI_stats_agg, newp);
            }
          else
            {
              mpiPi_cs_merge(csp, p);
            }
        }
    }

  return 1;
}

#ifndef ENABLE_API_ONLY		/* { */

static int
mpiPi_mergeResults ()
{
  int ac;
  callsite_stats_t **av;
  int totalCount = 0;
  int maxCount = 0;
  int retval = 1, sendval;
  callsite_stats_t *rawCallsiteData = NULL;

  /* gather local task data */
  mpiPi_stats_mt_cs_gather(&mpiPi.task_stats, &ac, &av);

  /* determine size of space necessary on collector */
  PMPI_Allreduce (&ac, &totalCount, 1, MPI_INT, MPI_SUM, mpiPi.comm);
  PMPI_Reduce (&ac, &maxCount, 1, MPI_INT, MPI_MAX, mpiPi.collectorRank,
               mpiPi.comm);
  if (mpiPi.collectorRank != mpiPi.rank) {
      maxCount = ac;
    }

  if (totalCount < 1)
    {
      if (mpiPi.rank == mpiPi.collectorRank)
        mpiPi_msg_warn
            ("Collector found no records to merge. Omitting report.\n");

      return 0;
    }

  /* Try to allocate space for max count of callsite info from all tasks  */
  rawCallsiteData =
      (callsite_stats_t *) calloc (maxCount, sizeof (callsite_stats_t));
  if (rawCallsiteData == NULL)
    {
      mpiPi_msg_warn
          ("Failed to allocate memory to collect callsite info");
      retval = 0;
    }

  /* gather global data at collector */
  if (mpiPi.rank == mpiPi.collectorRank)
    {
      int i;
      int ndx = 0;

#ifdef ENABLE_BFD
      if (mpiPi.appFullName != NULL)
        {
          if (open_bfd_executable (mpiPi.appFullName) == 0)
            mpiPi.do_lookup = 0;
        }
#elif defined(USE_LIBDWARF)
      if (mpiPi.appFullName != NULL)
        {
          if (open_dwarf_executable (mpiPi.appFullName) == 0)
            mpiPi.do_lookup = 0;
        }
#endif
#if defined(ENABLE_BFD) || defined(USE_LIBDWARF)
      else
        {
          mpiPi_msg_warn
              ("Failed to open executable.  The mpiP -x runtime flag may address this issue.\n");
          mpiPi.do_lookup = 0;
        }
#endif

      /* Open call site hash tables.  */
      mpiPi.global_callsite_stats = h_open (mpiPi.tableSize,
                                            mpiPi_callsite_stats_src_hashkey,
                                            mpiPi_callsite_stats_src_comparator);
      mpiPi.global_callsite_stats_agg = h_open (mpiPi.tableSize,
                                                mpiPi_callsite_stats_src_id_hashkey,
                                                mpiPi_callsite_stats_src_id_comparator);
      mpiPi_cs_cache_init();

      /* Clear global_mpi_time and global_mpi_size before accumulation in mpiPi_insert_callsite_records */
      mpiPi.global_mpi_time = 0.0;
      mpiPi.global_mpi_size = 0.0;

      if (retval == 1)
        {
          /* Insert local callsite information */
          for (ndx = 0; ndx < ac; ndx++)
            {
              mpiPi_insert_callsite_records (av[ndx]);
            }

          /* Collect remote pc data */
          for (i = 1; i < mpiPi.size; i++)	/* n-1 */
            {
              MPI_Status status;
              int count;

              /* okay in any order */
              PMPI_Probe (MPI_ANY_SOURCE, mpiPi.tag, mpiPi.comm, &status);
              PMPI_Get_count (&status, MPI_CHAR, &count);
              PMPI_Recv (rawCallsiteData, count, MPI_CHAR,
                         status.MPI_SOURCE, mpiPi.tag, mpiPi.comm, &status);
              count /= sizeof (callsite_stats_t);

              for (ndx = 0; ndx < count; ndx++)
                {
                  mpiPi_insert_callsite_records (&rawCallsiteData[ndx]);
                }
            }
        }
    }
  else
    {
      int ndx;
      for (ndx = 0; ndx < ac; ndx++)
        {
          bcopy (av[ndx],
                 &(rawCallsiteData[ndx]),
                 sizeof (callsite_stats_t));
        }
      PMPI_Send (rawCallsiteData, ac * sizeof (callsite_stats_t),
                 MPI_CHAR, mpiPi.collectorRank, mpiPi.tag, mpiPi.comm);
    }

  free (rawCallsiteData);

  if (mpiPi.rank == mpiPi.collectorRank && retval == 1)
    {
      if (mpiPi.collective_report == 0)
        mpiPi_msg_debug
            ("MEMORY : Allocated for global_callsite_stats     : %13ld\n",
             h_count (mpiPi.global_callsite_stats) * sizeof (callsite_stats_t));
      mpiPi_msg_debug
          ("MEMORY : Allocated for global_callsite_stats_agg : %13ld\n",
           h_count (mpiPi.global_callsite_stats_agg) *
           sizeof (callsite_stats_t));
    }

  /* TODO: need to free all these pointers as well. */
  free (av);

  if (mpiPi.rank == mpiPi.collectorRank)
    {
      if (mpiPi.do_lookup == 1)
        {
#ifdef ENABLE_BFD
		  /* clean up */
		  close_bfd_executable ();
#elif defined(USE_LIBDWARF)
		  close_dwarf_executable ();
#endif
        }
    }

  /*  Quadrics MPI does not appear to support MPI_IN_PLACE   */
  sendval = retval;
  PMPI_Allreduce (&sendval, &retval, 1, MPI_INT, MPI_MIN, mpiPi.comm);
  return retval;
}


static int
mpiPi_mergeCollectiveStats ()
{
  double *coll_time_results = NULL, *coll_time_local = NULL;
  size_t size;

  if (!mpiPi.do_collective_stats_report)
    {
      return 1;
    }

  if (mpiPi.collectorRank == mpiPi.rank){
      coll_time_results = (double *) malloc (sizeof(mpiPi.coll_time_stats));
    }

  mpiPi_stats_mt_coll_gather(&mpiPi.task_stats, &coll_time_local);

  /*  Collect Collective statistic data were used  */
  size = sizeof(mpiPi.pt2pt_send_stats) / sizeof(double);
  PMPI_Reduce (coll_time_local, coll_time_results,
               size, MPI_DOUBLE, MPI_SUM, mpiPi.collectorRank, mpiPi.comm);
  free (coll_time_local);

  if (mpiPi.collectorRank == mpiPi.rank){
      int i = 0, x, y, z;
      for (x = 0; x < MPIP_NFUNC; x++)
        for (y = 0; y < MPIP_COMM_HISTCNT; y++)
          for (z = 0; z < MPIP_SIZE_HISTCNT; z++)
            mpiPi.coll_time_stats[x][y][z] = coll_time_results[i++];
      free (coll_time_results);
    }
  return 1;
}


static int
mpiPi_mergept2ptStats ()
{
  double *pt2pt_send_results = NULL, *pt2pt_send_local = NULL;
  size_t size;


  if (!mpiPi.do_pt2pt_stats_report)
    {
      return 1;
    }

  if (mpiPi.collectorRank == mpiPi.rank){
      pt2pt_send_results = (double *) malloc (sizeof(mpiPi.pt2pt_send_stats));
    }
  mpiPi_stats_mt_pt2pt_gather(&mpiPi.task_stats, &pt2pt_send_local);

  /*  Collect Collective statistic data were used  */
  size = sizeof(mpiPi.pt2pt_send_stats) / sizeof(double);
  PMPI_Reduce (pt2pt_send_local, pt2pt_send_results,
               size, MPI_DOUBLE, MPI_SUM, mpiPi.collectorRank, mpiPi.comm);
  free(pt2pt_send_local);

  if (mpiPi.collectorRank == mpiPi.rank)
    {
      int i = 0, x, y, z;
      for (x = 0; x < mpiPi_DEF_END - mpiPi_BASE; x++)
        for (y = 0; y < 32; y++)
          for (z = 0; z < 32; z++)
            mpiPi.pt2pt_send_stats[x][y][z] = pt2pt_send_results[i++];

      free (pt2pt_send_results);
    }

  return 1;
}


static void
mpiPi_publishResults (int report_style)
{
  FILE *fp = NULL;
  static int printCount = 0;

  if (mpiPi.collectorRank == mpiPi.rank)
    {

      /* Generate output filename, and open */
      do
        {
          printCount++;
          snprintf (mpiPi.oFilename, 256, "%s/%s.%d.%d.%d.mpiP",
                    mpiPi.outputDir, mpiPi.appName, mpiPi.size, mpiPi.procID,
                    printCount);
        }
      while (access (mpiPi.oFilename, F_OK) == 0);

      fp = fopen (mpiPi.oFilename, "w");

      if (fp == NULL)
        {
          mpiPi_msg_warn ("Could not open [%s], writing to stdout\n",
                          mpiPi.oFilename);
          fp = stdout;
        }
      else
        {
          mpiPi_msg ("\n");
          mpiPi_msg ("Storing mpiP output in [%s].\n", mpiPi.oFilename);
          mpiPi_msg ("\n");
        }
    }
  mpiPi_profile_print (fp, report_style);
  PMPI_Barrier (mpiPi.comm);
  if (fp != stdout && fp != NULL)
    {
      fclose (fp);
    }
}


/*
 * mpiPi_collect_basics() - all tasks send their basic info to the
 * collectorRank.
 */
static void
mpiPi_collect_basics (int report_style)
{
  mpiPi_msg_debug ("Collect Basics\n");

  if (mpiPi.rank == mpiPi.collectorRank)
    {
      /* In the case where multiple reports are generated per run,
         only allocate memory for global_task_info once */
      if (mpiPi.global_task_app_time == NULL)
        {
          mpiPi.global_task_app_time =
              (double *) calloc (mpiPi.size, sizeof (double));

          if (mpiPi.global_task_app_time == NULL)
            mpiPi_abort
                ("Failed to allocate memory for global_task_app_time");

          mpiPi_msg_debug
              ("MEMORY : Allocated for global_task_app_time :          %13ld\n",
               mpiPi.size * sizeof (double));
        }

      bzero (mpiPi.global_task_app_time, mpiPi.size * sizeof (double));

      if (mpiPi.global_task_mpi_time == NULL)
        {
          mpiPi.global_task_mpi_time =
              (double *) calloc (mpiPi.size, sizeof (double));

          if (mpiPi.global_task_mpi_time == NULL)
            mpiPi_abort
                ("Failed to allocate memory for global_task_mpi_time");

          mpiPi_msg_debug
              ("MEMORY : Allocated for global_task_mpi_time :          %13ld\n",
               mpiPi.size * sizeof (double));
        }

      bzero (mpiPi.global_task_mpi_time, mpiPi.size * sizeof (double));

      //  Only allocate hostname storage if we are doing a verbose report
      if (mpiPi.global_task_hostnames == NULL
          && (report_style == mpiPi_style_verbose
              || report_style == mpiPi_style_both))
        {
          mpiPi.global_task_hostnames =
              (mpiPi_hostname_t *) calloc (mpiPi.size,
                                           sizeof (char) *
                                           MPIPI_HOSTNAME_LEN_MAX);

          if (mpiPi.global_task_hostnames == NULL)
            mpiPi_abort
                ("Failed to allocate memory for global_task_hostnames");

          mpiPi_msg_debug
              ("MEMORY : Allocated for global_task_hostnames :          %13ld\n",
               mpiPi.size * sizeof (char) * MPIPI_HOSTNAME_LEN_MAX);
        }

      if (mpiPi.global_task_hostnames != NULL)
        bzero (mpiPi.global_task_hostnames,
               mpiPi.size * sizeof (char) * MPIPI_HOSTNAME_LEN_MAX);
    }

  PMPI_Gather (&mpiPi.cumulativeTime, 1, MPI_DOUBLE,
               mpiPi.global_task_app_time, 1, MPI_DOUBLE,
               mpiPi.collectorRank, mpiPi.comm);

  if (report_style == mpiPi_style_verbose || report_style == mpiPi_style_both)
    {
      PMPI_Gather (mpiPi.hostname, MPIPI_HOSTNAME_LEN_MAX, MPI_CHAR,
                   mpiPi.global_task_hostnames, MPIPI_HOSTNAME_LEN_MAX,
                   MPI_CHAR, mpiPi.collectorRank, mpiPi.comm);
    }

  return;
}


void
mpiPi_generateReport (int report_style)
{
  mpiP_TIMER dur;
  mpiPi_TIME timer_start, timer_end;
  int mergeResult;

  if (mpiPi.enabled)
    {
      mpiPi_stats_mt_timer_stop(&mpiPi.task_stats);
    }
  mpiPi_stats_mt_merge(&mpiPi.task_stats);
  mpiPi.cumulativeTime = mpiPi_stats_mt_cum_time(&mpiPi.task_stats);
  assert (mpiPi.cumulativeTime >= 0);
  if (mpiPi.enabled)
    {
      mpiPi_stats_mt_timer_start(&mpiPi.task_stats);
    }

  if (time (&mpiPi.stop_timeofday) == (time_t) - 1)
    {
      mpiPi_msg_warn ("Could not get time of day from time()\n");
    }

  /* collect results and publish */
  mpiPi_msg_debug0 ("starting collect_basics\n");

  mpiPi_GETTIME (&timer_start);
  mpiPi_collect_basics (report_style);
  mpiPi_GETTIME (&timer_end);
  dur = (mpiPi_GETTIMEDIFF (&timer_end, &timer_start) / 1000000.0);

  mpiPi_msg_debug0 ("TIMING : collect_basics_time is %12.6f\n", dur);

  mpiPi_msg_debug0 ("starting mergeResults\n");

  mpiPi_GETTIME (&timer_start);
  mergeResult = mpiPi_mergeResults ();
  if (mergeResult == 1 && mpiPi.reportStackDepth == 0)
    mergeResult = mpiPi_insert_MPI_records ();
  if (mergeResult == 1)
    mergeResult = mpiPi_mergeCollectiveStats ();
  if (mergeResult == 1)
    mergeResult = mpiPi_mergept2ptStats ();
  mpiPi_GETTIME (&timer_end);
  dur = (mpiPi_GETTIMEDIFF (&timer_end, &timer_start) / 1000000.0);

  mpiPi_msg_debug0 ("TIMING : merge time is          %12.6f\n", dur);
  mpiPi_msg_debug0 ("starting publishResults\n");

  if (mergeResult == 1)
    {
      mpiPi_GETTIME (&timer_start);
      if (mpiPi.report_style == mpiPi_style_both)
        {
          mpiPi_publishResults (mpiPi_style_concise);
          mpiPi_publishResults (mpiPi_style_verbose);
        }
      else
        mpiPi_publishResults (report_style);
      mpiPi_GETTIME (&timer_end);
      dur = (mpiPi_GETTIMEDIFF (&timer_end, &timer_start) / 1000000.0);
      mpiPi_msg_debug0 ("TIMING : publish time is        %12.6f\n", dur);
    }
}


void
mpiPi_finalize ()
{
  // if (mpiPi.disable_finalize_report == 0)
    // mpiPi_generateReport (mpiPi.report_style);

  mpiPi_stats_mt_fini(&mpiPi.task_stats);

  if (mpiPi.global_task_app_time != NULL)
    free (mpiPi.global_task_app_time);

  if (mpiPi.global_task_mpi_time != NULL)
    free (mpiPi.global_task_mpi_time);

  if (mpiPi.global_task_hostnames != NULL)
    free (mpiPi.global_task_hostnames);

  // printf("mpiP: rank %d writing trace, %d bytes\n",mpiPi.rank, mpiPi.event_list.size);
  fwrite(mpiPi.event_list.data, sizeof(char), mpiPi.event_list.size,mpiPi.recfile);
  fclose(mpiPi.recfile);
  // list_free(&mpiPi.event_list);



  /*  Could do a lot of housekeeping before calling PMPI_Finalize()
   *  but is it worth the additional work?
   *  For instance:
   h_gather_data (mpiPi.global_callsite_stats_agg, &ac, (void ***) &av);
   for (i = 0; (i < 20) && (i < ac); i++)
   {
   if (av[i]->siteData != NULL )
   free (av[i]->siteData);
   }
   */

  return;
}


void
mpiPi_update_callsite_stats (mpiPi_mt_stat_tls_t *tls,
                             unsigned op, unsigned rank, void **pc,
                             double dur, double sendSize, double ioSize,
                             double rmaSize)
{
  int i;
  callsite_stats_t *csp = NULL;
  callsite_stats_t key;

  mpiPi_stats_mt_cs_upd(tls, op, rank, pc, dur,
                        sendSize, ioSize, rmaSize);
}

void
mpiPi_update_collective_stats (mpiPi_mt_stat_tls_t *tls, int op, double dur, double size,
                               MPI_Comm * comm)
{
  mpiPi_stats_mt_coll_upd(tls, op, dur, size, comm);
}

void
mpiPi_update_pt2pt_stats (mpiPi_mt_stat_tls_t *tls,
                          int op, double dur, double size,
                          MPI_Comm * comm)
{
  mpiPi_stats_mt_pt2pt_upd(tls, op, dur, size, comm);
}

#endif /* } ifndef ENABLE_API_ONLY */



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
