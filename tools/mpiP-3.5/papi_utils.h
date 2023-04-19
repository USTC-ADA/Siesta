#include <malloc.h>
#include <stdlib.h>
#include <string.h>
#define PAPIEVENT_ENVIRONMENT_VARIABLE "PAPI_MON_EVENTS"
extern long long ** values;
extern int EventSet;
extern int event_count;

long long** allocate_values_space(int num_tests, int num_events) {
    long long **values;
	int i;

	values =
		( long long ** ) malloc( ( size_t ) num_tests *
								 sizeof ( long long * ) );
	if ( values == NULL ) {
		printf("error! cannot allocate memory\n");
        exit( 1 );
    }
	memset( values, 0x0, ( size_t ) num_tests * sizeof ( long long * ) );

	for ( i = 0; i < num_tests; i++ ) {
		values[i] =
			( long long * ) malloc( ( size_t ) num_events *
									sizeof ( long long ) );
		if ( values[i] == NULL ) {
            printf("error! cannot allocate memory\n");
        	exit( 1 );
        }
		memset( values[i], 0x00, ( size_t ) num_events * sizeof ( long long ) );
	}
	return ( values );
}

char** read_PAPIEvents_from_environment_variables(int* event_count) {
	char *pathvar = getenv(PAPIEVENT_ENVIRONMENT_VARIABLE);
    // printf("%s\n", pathvar);
	char** res;
	int count = 0, find = 0; int i = 0;
	for (i = 0; i < strlen(pathvar); i++) {
		if (pathvar[i] != ':' && find == 0) {
			count++;
			find = 1;
		} else if (pathvar[i] == ':' && find == 1) {
			find = 0;
		}
	}
    // printf("%d\n", count);
	res = (char**) malloc((count)*sizeof(char*));
	int start=0;
	int res_count = 0;
	for (i = 0; i < strlen(pathvar); i++) {
		if (pathvar[i] != ':' && find == 0) {
			find = 1;
			start = i;
            // printf("start = %d\n", start);
		} else if (pathvar[i] == ':' && find == 1) {
            // printf("end = %d\n", i);
			find = 0;
			res[res_count] = (char*)malloc((i-start+1)*sizeof(char));
			memset(res[res_count], 0, (i-start+1));
            memcpy(res[res_count], pathvar+start, i-start);
            res_count++;
		}
	}
	if (find==1) {
		res[res_count] = (char*)malloc((i-start+1)*sizeof(char));
		memset(res[res_count], 0, (i-start+1));
        memcpy(res[res_count], pathvar+start, strlen(pathvar)-start);
        res_count++;
	}
	*event_count = count;
	// for (int i = 0; i < count; i++) {
	// 	printf("%s\n", res[i]);
	// }
	return (res);
}

