#include <malloc.h>
#include <string.h>

#ifndef LIST
#define LIST
typedef struct
{
  int size;
  int capacity;
  char *data;
} list_t;
#endif
void list_init(list_t *list)
{
  list->size = 0;
  list->capacity = 65536;
  list->data = (char*)malloc(list->capacity*sizeof(char));
  if(list->data == NULL)
  {
    printf("error: insufficient memory for initializing list\n");
  }
}
void list_ppush(list_t *list, char *item)
{
  int item_size;
  item_size = strlen(item);
  // printf("size: %d, capacity: %d, itemsize: %d, item: %s",list->size, list->capacity, item_size, item); //debug
  if(list->size + item_size >= list->capacity)
  {
    list->capacity = list->capacity * 2;
    list->data = (char*)realloc(list->data, list->capacity*sizeof(char));
  }
  if(list->data == NULL)
  {
    printf("error: insufficient memory for pushing an item\n");
  }
  else
  {
    strcpy(&list->data[list->size], item);
    list->size = list->size + item_size;
  }
}
void list_finalize(list_t *list)
{
  free(list->data);
}
